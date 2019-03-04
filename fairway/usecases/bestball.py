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
    def number_of_best_balls(self):
        return self._number_of_best_balls

    @property
    def number_of_holes(self):
        return self._number_of_holes

    def play_individual_game(self, players: Iterable[Player]):
        self._play(count_hole_wins(), players)

    def play_team_game(self, players: Iterable[Player], teams: Iterable[Team]):
        self._play(count_game_wins(), players, teams)

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

        for tot_scores, number_of_wins in limit(self.simulator.number_of_iterations, self._scenario(all_allowances,
                                                                                                    player_handicaps, teams_as_player_indexes,
                                                                                                    counter_fn)):
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

    def _scenario(self, allowances: np.ndarray, player_handicaps: Iterable[int], teams=None, aggregate_by=None):
        while True:
            sample = self.simulator.sample_game_scenario(player_handicaps, self.number_of_holes)
            s = np.add(self.simulator.sample_game_scenario(player_handicaps, self.number_of_holes), allowances)
            if teams:
                s = self.to_team_scenario(s, teams)

            if aggregate_by:
                yield aggregate_by.send(s)
            else:
                yield s

    def to_team_scenario(self, players_scenarios, teams):
        n_players, n_holes = players_scenarios.shape
        team_scenarios = np.zeros((len(teams), n_holes), dtype=int)
        players_scenarios_tr = players_scenarios.transpose()
        for team_index, player_indexes in enumerate(teams):
            for hole in range(n_holes):
                all_team_scores = np.asarray(itemgetter(*player_indexes)(players_scenarios_tr[hole]), dtype=int)
                if self._number_of_best_balls < len(player_indexes):
                    indexes = np.argpartition(all_team_scores, self.number_of_best_balls)
                    team_best_scores_sum = np.sum(all_team_scores[indexes[:self.number_of_best_balls]])
                else:
                    team_best_scores_sum = np.sum(all_team_scores)
                team_scenarios[team_index, hole] = team_best_scores_sum

        return team_scenarios


def _update_scores(game_scenario, current_tot_scores):
    n_players, _ = game_scenario.shape
    scores = np.zeros(n_players)
    for player_index in range(n_players):
        scores[player_index] = np.sum(game_scenario[player_index, :])

    tot_scores = np.add(current_tot_scores, scores)
    return scores, tot_scores


@coroutine
def count_hole_wins():
    """

    :return: counts the
    """
    tot_scores = None
    curr_counts = dict()
    while True:
        game_scenario = (yield (tot_scores, curr_counts))

        # Update Scores
        if tot_scores is None:
            n_players, _ = game_scenario.shape
            tot_scores = np.zeros(n_players, dtype=int)
        _, tot_scores = _update_scores(game_scenario, tot_scores)

        # Update Hole Win Counts
        _, n_holes = game_scenario.shape
        for hole in range(n_holes):
            hole_scores = game_scenario[:, hole]
            winning_score = np.min(hole_scores)
            winners = [idx for idx, score in enumerate(hole_scores) if score == winning_score]
            for winner in winners:
                curr_counts[winner] = curr_counts.get(winner, 0) + (1.0 / len(winners))


@coroutine
def count_game_wins():
    """

    :return:
    """
    tot_scores = None
    curr_counts = dict()
    while True:
        game_scenario = (yield (tot_scores, curr_counts))

        # Update Scores
        if tot_scores is None:
            n_players, _ = game_scenario.shape
            tot_scores = np.zeros(n_players, dtype=int)
        scores, tot_scores = _update_scores(game_scenario, tot_scores)

        # Update Game Win Counts
        winners = game_winners(scores)
        for winner in winners:
            curr_counts[winner] = curr_counts.get(winner, 0) + (1.0/len(winners))


def game_winners(scores):
    winning_score = np.min(scores)
    return tuple(idx for idx in range(len(scores)) if scores[idx] == winning_score)
