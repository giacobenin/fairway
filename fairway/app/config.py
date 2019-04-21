from fairway.app.datasets import CSVDataset
from fairway.domain.game import Game
from fairway.usecases.bestball import BestBallGame
from fairway.usecases.dataset import Dataset
from fairway.usecases.fairness import FairnessEvaluator, MaxDifference
from fairway.usecases.simulator import Simulator, MonteCarloSimulator
from fairway.usecases.swaps import SwapGenerator, UnfairTeamsPairsWorsePlayersOnly, Swapper, SimpleSwapper


def create_config(distributions, number_of_iterations: int, tolerance: float=0.1):
    """

    :param distributions:
    :param number_of_iterations:
    :return:
    """
    assert tolerance > 0.0
    assert tolerance < 1.0

    def config(binder):
        binder.bind(SwapGenerator, UnfairTeamsPairsWorsePlayersOnly())
        binder.bind(FairnessEvaluator, MaxDifference(tolerance))
        binder.bind(Dataset, CSVDataset(distributions))
        binder.bind(Simulator, MonteCarloSimulator(number_of_iterations))
        binder.bind_to_constructor(Game, BestBallGame)
        binder.bind_to_constructor(Swapper, SimpleSwapper)
    return config
