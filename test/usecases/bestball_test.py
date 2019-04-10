
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

    game = BestBallGameFake(3)
    scores_by_hole, wins_by_hole = game._play_individual_game(scenario, scores_by_hole, wins_by_hole)
    np.testing.assert_array_equal(scores_by_hole, scenario)
    np.testing.assert_array_equal(wins_by_hole, np.array([
        [0.5, 1/3, 0],
        [0,   0,   0],
        [0.5, 1/3, 0],
        [0,   1/3, 1]
        ], np.float))

