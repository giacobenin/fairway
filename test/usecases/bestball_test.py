
import numpy as np
from fairway.usecases.bestball import BestBallGame


class BestBallGameFake(BestBallGame):
    def __init__(self, number_of_holes: int = 18, number_of_best_balls: int = 1):
        super().__init__(number_of_holes, number_of_best_balls)


def test_play_individual_game():
    scenario = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [1, 2, 3],
        [2, 2, 2]
        ], np.int32)

    number_of_players, number_of_holes = scenario.shape
    scores_by_hole = np.zeros((number_of_players, number_of_holes), dtype=np.int32)
    wins_by_hole = np.zeros((number_of_players, number_of_holes), dtype=np.float)

    game = BestBallGameFake(number_of_holes)
    scores_by_hole, wins_by_hole = game._play_individual_game(scenario, scores_by_hole, wins_by_hole)
    np.testing.assert_array_equal(scores_by_hole, scenario)
    np.testing.assert_array_equal(wins_by_hole, np.array([
        [0.5, 1/3, 0],
        [0,   0,   0],
        [0.5, 1/3, 0],
        [0,   1/3, 1]
        ], np.float))


def test_play_team_game_one_best_ball():
    scenario = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [1, 2, 3],
        [2, 2, 2]
    ], np.int32)

    _, number_of_holes = scenario.shape
    teams = [(0, 1), (2, 3)]
    team_scores_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.int32)
    number_of_wins_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.float)

    game = BestBallGameFake(number_of_holes, 1)
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
    scenario = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [1, 2, 3],
        [2, 2, 2]
    ], np.int32)

    _, number_of_holes = scenario.shape
    teams = [(0, 1), (2, 3)]
    team_scores_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.int32)
    number_of_wins_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.float)

    game = BestBallGameFake(number_of_holes, 2)
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
    scenario = np.array([
        [1, 2, 3],
        [9, 9, 9],
        [4, 5, 6],
        [9, 9, 9],
        [1, 2, 3],
        [2, 2, 2]
    ], np.int32)

    _, number_of_holes = scenario.shape
    teams = [(0, 1, 2), (3, 4, 5)]
    team_scores_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.int32)
    number_of_wins_by_hole = np.zeros((len(teams), number_of_holes), dtype=np.float)

    game = BestBallGameFake(number_of_holes, 2)
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