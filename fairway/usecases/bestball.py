from typing import Iterable

import inject

import numpy as np

from operator import itemgetter
from fairway.domain.game import Game
from fairway.domain.player import Player
from fairway.domain.playing_entity import PlayingEntity
from fairway.domain.team import Team
from fairway.usecases.simulator import Simulator
from fairway.util.corutine import coroutine, limit


class BestBallGame(Game):

    simulator = inject.attr(Simulator)

    def __init__(self, number_of_holes: int = 18, number_of_best_balls: int = 1):
        assert isinstance(number_of_holes, int)
        assert isinstance(number_of_best_balls, int)

        self._number_of_holes = number_of_holes
        self._number_of_best_balls = number_of_best_balls

    @property
    def number_of_best_balls(self) -> int:
        return self._number_of_best_balls

    @property
    def number_of_holes(self) -> int:
        return self._number_of_holes

    def play_individual_game(self, players: Iterable[Player]):
        self._play(count_hole_wins(), players)

    def play_team_game(self, players: Iterable[Player], teams: Iterable[Team]):
        self._play(count_game_wins(), players, teams)

    def _play2(self, counter_fn, players, teams=None) -> Iterable[PlayingEntity]:
        def _scenario(allowances: np.ndarray, player_handicaps: Iterable[int], teams=None, aggregate_by=None):
            while True:
                sample = self.simulator.sample_game_scenario(player_handicaps, self.number_of_holes)
                s = np.add(sample, allowances)
                if teams:
                    s = self.to_team_scenario(s, teams)
                yield s

        # Vectorize objects for faster processing:

        # 1. Sort players by teams (simplifies slicing by group)
        players_by_team = sorted(players, key=lambda p: p.team_id)
        index_to_player_id = dict()
        player_id_to_index = dict()
        for index, player in enumerate(players_by_team):
            index_to_player_id[index] = player.id
            player_id_to_index[player.id] = index
        player_handicaps = tuple(player.handicap for player in players_by_team)
        all_allowances = np.vstack((player.allowances_by_hole for player in players_by_team))  # Pre-compute allowance matrix
        assert (all_allowances.shape == (len(players_by_team), self._number_of_holes))

        # Create list of tuples, each of them containing the indexes of its members
        teams_as_player_indexes = list()
        for team in teams:
            teams_as_player_indexes.append(tuple(player_id_to_index[player.id] for player in team.members))
            teams_as_player_indexes = [sorted(t) for t in teams_as_player_indexes]

        # Algorithm
        individual = True
        self.simulator.reset()
        tot_scores = None
        number_of_wins = dict()
        next_scenario = _scenario(all_allowances, player_handicaps, teams_as_player_indexes, counter_fn)
        player_scores_by_hole = np.zeros(type=float)
        number_of_wins_by_hole = np.zeros(type=float)
        for count, scenario in enumerate(next_scenario):
            if count >= self.simulator.number_of_iterations:
                break
            player_scores_by_hole = np.add(player_scores_by_hole, scenario)
            for i in range(18):
                hole_scores = scenario[:, i]
                if individual:
                    winning_score = min(hole_scores)
                    winning_players = tuple(idx for idx in range(len(hole_scores)) if hole_scores[idx] == winning_score)
                    for winning_player in winning_players:
                        number_of_wins_by_hole[winning_player, i] += 1.0 / float(len(winning_players))

    def _play_individual_or_team_games(self, allowances, player_handicaps, teams=None):
        """
        Runs self.simulator.number_of_iterations games and returns average scores by hole, prob. of winning by hole,
        average game score, prob. of winning game.

        :param allowances:
        :param player_handicaps:
        :param teams:
        :return:
        """
        fn, rows = (self._play_team_game, len(teams)) if teams else (self._play_individual_game, len(player_handicaps))
        scores_by_hole = np.zeros((rows, self.number_of_holes), dtype=float)
        wins_by_hole = np.zeros((rows, self.number_of_holes), dtype=float)

        for count, sample in enumerate(self.simulator.sample_game_scenario(player_handicaps, self.number_of_holes)):
            if count >= self.simulator.number_of_iterations:
                break
            scenario = np.add(sample, allowances)

            scores_by_hole, wins_by_hole = fn(scenario, scores_by_hole, wins_by_hole)

        average_game_score = np.divide(np.sum(scores_by_hole, axis=1), self.simulator.number_of_iterations)
        scores_by_hole = np.divide(scores_by_hole, self.simulator.number_of_iterations)
        prob_of_winning_by_hole = np.divide(wins_by_hole, self.simulator.number_of_iterations)
        return scores_by_hole, average_game_score, prob_of_winning_by_hole

    def _play_individual_game(self, scenario, player_scores_by_hole, number_of_wins_by_hole):
        """
        It updates player_scores_by_hole, and number_of_wins_by_hole (to avoid creating a new array)!!!

        :param scenario: the current scenario (scores of all players on all holes for one iteration)
        :param player_scores_by_hole:
        :param number_of_wins_by_hole:
        :return:
        """
        player_scores_by_hole = np.add(player_scores_by_hole, scenario)
        return player_scores_by_hole, self.count_wins_by_hole(scenario, number_of_wins_by_hole)

    def _play_team_game(self, scenario, teams, team_scores_by_hole, number_of_wins_by_hole):
        """
        It updates player_scores_by_hole, and number_of_wins_by_hole (to avoid creating a new array)!!!

        :param scenario:
        :param teams:
        :param team_scores_by_hole:
        :param number_of_wins_by_hole:
        :return:
        """
        def get_team_score_on_hole(current_team_scenario, current_hole):
            all_members_scores = current_team_scenario[:, current_hole]
            current_team_scenario_by_hole = current_team_scenario[:, current_hole]
            if self.number_of_best_balls >= len(current_team_scenario_by_hole):
                idx = [range(len(current_team_scenario_by_hole))]
            else:
                idx = np.argpartition(current_team_scenario_by_hole, self.number_of_best_balls)
            return sum(all_members_scores[idx[:self.number_of_best_balls]])

        team_scenario = np.zeros((len(teams), self.number_of_holes), dtype=float)
        for i, team in enumerate(teams):
            all_members_scenario = scenario[team[0]:team[-1]+1, :]  # This expects team members' scores in contiguous rows
            team_scenario[i] = [get_team_score_on_hole(all_members_scenario, hole) for hole in range(self.number_of_holes)]

        self.count_wins_by_hole(team_scenario, number_of_wins_by_hole)
        return np.add(team_scores_by_hole, team_scenario), number_of_wins_by_hole

    def count_wins_by_hole(self, scenario, number_of_wins_by_hole):
        for i in range(self.number_of_holes):
            hole_scores = scenario[:, i]
            winning_score = min(hole_scores)
            winning_entities = tuple(idx for idx in range(len(hole_scores)) if hole_scores[idx] == winning_score)
            for winning_entity in winning_entities:
                number_of_wins_by_hole[winning_entity, i] += 1.0 / float(len(winning_entities))
        return number_of_wins_by_hole


    def _play(self, counter_fn, players, teams=None) -> Iterable[PlayingEntity]:
        # Vectorize objects for faster processing:
        # Players -> enumerable of handicaps
        # Teams -> enumerable of indexes
        # Create allowance matrix
        teams_as_player_indexes = None
        if teams:
            teams_as_player_indexes = list()
            player_id_to_index = dict()
            for index, player in enumerate(players):
                player_id_to_index[player.id] = index
            for team in teams:
                teams_as_player_indexes.append(tuple(player_id_to_index[player.id] for player in team.members))
        player_handicaps = tuple(player.handicap for player in players)
        all_allowances = np.vstack((player.allowances_by_hole for player in players))  # Pre-compute allowance matrix
        assert (all_allowances.shape == (len(players), self._number_of_holes))

        # Algorithm
        self.simulator.reset()
        tot_scores = None
        number_of_wins = dict()
        scenario_gen = self._scenario(all_allowances, player_handicaps, teams_as_player_indexes, counter_fn)
        for tot_scores, number_of_wins in limit(self.simulator.number_of_iterations, scenario_gen):
            pass
        counter_fn.close()

        total = sum(v for k, v in number_of_wins.items())
        win_probabilities = np.zeros(len(teams_as_player_indexes) if teams_as_player_indexes else len(players))
        for k, v in number_of_wins.items():
            win_probabilities[k] = v / total

        scores = np.round(tot_scores / self.simulator.number_of_iterations, 2)

        # Update entities
        for entity, score, win_prob in zip(teams if teams else players, scores, win_probabilities):
            entity.expected_score = score
            entity.prob_of_winning = win_prob

        return teams if teams else players









