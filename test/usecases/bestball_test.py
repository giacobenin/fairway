import numpy as np
from fairway.usecases.bestball import BestBallGame
from fairway.usecases.simulator import Simulator

scenario = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [1, 2, 3],
    [2, 2, 2]
], np.int32)


class FakeSimulator(Simulator):

    def __init__(self, constant_scenario, number_of_iterations: int):
        super().__init__(number_of_iterations)
        self.scenario = constant_scenario

    @property
    def number_of_iterations(self):
        return self._number_of_iterations

    def sample_game_scenario(self, players = None, number_of_holes = None) -> np.ndarray:
        for i in range(self.number_of_iterations):
            yield self.scenario

    def reset(self):
        pass


class FakeBestBallGame(BestBallGame):
    def __init__(self, number_of_holes: int = 18, number_of_best_balls: int = 1, simulator=None):
        super().__init__(number_of_holes, number_of_best_balls)
        self.simulator = simulator


def test_play_individual_game():
    number_of_players, number_of_holes = scenario.shape
    scores_by_hole = np.zeros((number_of_players, number_of_holes), dtype=np.int32)
    wins_by_hole = np.zeros((number_of_players, number_of_holes), dtype=np.float)

    game = FakeBestBallGame(number_of_holes)
    scores_by_hole, wins_by_hole = game._play_individual_game(scenario, scores_by_hole, wins_by_hole)
    np.testing.assert_array_equal(scores_by_hole, scenario)
    np.testing.assert_array_equal(wins_by_hole, np.array([
        [0.5, 1/3, 0],
        [0,   0,   0],
        [0.5, 1/3, 0],
        [0,   1/3, 1]
        ], np.float))


def test_play_team_game_one_best_ball():
    _, number_of_holes = scenario.shape
    teams = [(0, 1), (2, 3)]
    team_scores_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.int32)
    number_of_wins_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.float)

    game = FakeBestBallGame(number_of_holes, 1)
    team_scores_by_hole, number_of_wins_by_hole = game._play_team_game(scenario, teams, team_scores_by_hole,
                                                                       number_of_wins_by_hole)

    np.testing.assert_array_equal(team_scores_by_hole, np.array([
        [1,   2, 3],
        [1,   2, 2],
        ], np.int32))
    np.testing.assert_array_equal(number_of_wins_by_hole, np.array([
        [0.5, 0.5, 0],
        [0.5, 0.5, 1],
    ], np.float))


def test_play_team_game_two_best_ball():
    _, number_of_holes = scenario.shape
    teams = [(0, 1), (2, 3)]
    team_scores_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.int32)
    number_of_wins_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.float)

    game = FakeBestBallGame(number_of_holes, 2)
    team_scores_by_hole, number_of_wins_by_hole = game._play_team_game(scenario, teams, team_scores_by_hole,
                                                                       number_of_wins_by_hole)

    np.testing.assert_array_equal(team_scores_by_hole, np.array([
        [5,   7, 9],
        [3,   4, 5],
        ], np.int32))
    np.testing.assert_array_equal(number_of_wins_by_hole, np.array([
        [0, 0, 0],
        [1, 1, 1],
    ], np.float))


def test_play_team_game_two_best_ball_bis():
    larger_scenario = np.array([
        [1, 2, 3],
        [9, 9, 9],
        [4, 5, 6],
        [9, 9, 9],
        [1, 2, 3],
        [2, 2, 2]
    ], np.int32)

    _, number_of_holes = larger_scenario.shape
    teams = [(0, 1, 2), (3, 4, 5)]
    team_scores_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.int32)
    number_of_wins_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.float)

    game = FakeBestBallGame(number_of_holes, 2)
    team_scores_by_hole, number_of_wins_by_hole = game._play_team_game(larger_scenario, teams, team_scores_by_hole,
                                                                       number_of_wins_by_hole)

    np.testing.assert_array_equal(team_scores_by_hole, np.array([
        [5,   7, 9],
        [3,   4, 5],
        ], np.int32))
    np.testing.assert_array_equal(number_of_wins_by_hole, np.array([
        [0, 0, 0],
        [1, 1, 1],
    ], np.float))


def test_play_individual_or_team_games_individual():
    number_of_players, number_of_holes = scenario.shape
    allowances = np.zeros(scenario.shape)
    fake_handicaps = [i for i in range(number_of_players)]
    game = FakeBestBallGame(number_of_holes, 1, FakeSimulator(scenario, 3))

    scores_by_hole, average_game_score, prob_of_winning_by_hole = game._play_individual_or_team_games(allowances,
                                                                                                      fake_handicaps)

    np.testing.assert_array_equal(scores_by_hole, scenario)
    np.testing.assert_array_equal(average_game_score, np.array([6, 15, 6, 6], np.float))
    np.testing.assert_array_equal(prob_of_winning_by_hole, np.array([
        [0.5, 1 / 3, 0],
        [0, 0, 0],
        [0.5, 1 / 3, 0],
        [0, 1 / 3, 1]
    ], np.float))


def test_play_individual_or_team_games_team():
    number_of_players, number_of_holes = scenario.shape
    allowances = np.zeros(scenario.shape)
    fake_handicaps = [i for i in range(number_of_players)]
    teams = [(0, 1), (2, 3)]
    game = FakeBestBallGame(number_of_holes, 2, FakeSimulator(scenario, 3))

    scores_by_hole, average_game_score, prob_of_winning_by_hole = game._play_individual_or_team_games(allowances,
                                                                                                      fake_handicaps,
                                                                                                      teams)

    np.testing.assert_array_equal(scores_by_hole, np.array([
        [5, 7, 9],
        [3, 4, 5],
    ], np.int32))
    np.testing.assert_array_equal(average_game_score, np.array([21, 12], np.float))
    np.testing.assert_array_equal(prob_of_winning_by_hole, np.array([
        [0, 0, 0],
        [1, 1, 1],
    ], np.float))
