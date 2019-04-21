from typing import Iterable
import inject
import numpy as np
from fairway.domain.game import Game
from fairway.domain.metrics import Metrics
from fairway.domain.player import Player
from fairway.domain.playing_entity import PlayingEntity
from fairway.domain.team import Team
from fairway.usecases.game_model import GameVectorizedModel
from fairway.usecases.simulator import Simulator


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
        return self._play(players)

    def play_team_game(self, players: Iterable[Player], teams: Iterable[Team]):
        return self._play(players, teams)

    def _play(self, players, teams=None) -> Iterable[PlayingEntity]:

        # Vectorize objects for faster processing
        model = GameVectorizedModel(players, teams)

        metrics = self._play_individual_or_team_games(model.allowances, model.handicaps, model.teams)

        for entity in teams if teams else players:
            id_to_index = model.team_id_to_index if teams else model.player_id_to_index
            idx = id_to_index[entity.id]
            entity.metrics = Metrics(
                metrics.score_by_hole[idx, :],
                metrics.avg_score[idx],
                metrics.win_prob_by_hole[idx, :],
                metrics.win_prob[idx]
            )

    def _play_individual_or_team_games(self, allowances, player_handicaps, teams=None):
        """
        Runs self.simulator.number_of_iterations games and returns average scores by hole, prob. of winning by hole,
        average game score, prob. of winning game.

        :param allowances:
        :param player_handicaps:
        :param teams:
        :return:
        """
        rows = len(teams) if teams else len(player_handicaps)
        scores_by_hole = np.zeros((rows, self.number_of_holes), dtype=float)
        wins_by_hole = np.zeros((rows, self.number_of_holes), dtype=float)

        for _ in range(self.simulator.number_of_iterations):
            sample = self.simulator.sample_game_scenario(player_handicaps, self.number_of_holes)
            scenario = np.add(sample, allowances)

            if teams:
                scores_by_hole, wins_by_hole = self._play_team_game(scenario, teams, scores_by_hole, wins_by_hole)
            else:
                scores_by_hole, wins_by_hole = self._play_individual_game(scenario, scores_by_hole, wins_by_hole)

        n_iterations = float(self.simulator.number_of_iterations)

        average_game_score = np.divide(np.sum(scores_by_hole, axis=1), self.simulator.number_of_iterations)
        scores_by_hole /= n_iterations     #np.divide(scores_by_hole, )

        prob_of_winning = np.divide(wins_by_hole.sum(axis=1), n_iterations * float(self.number_of_holes))
        prob_of_winning_by_hole = np.divide(wins_by_hole, n_iterations)

        return Metrics(scores_by_hole, average_game_score, prob_of_winning_by_hole, prob_of_winning)

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
