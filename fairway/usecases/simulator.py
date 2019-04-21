from abc import ABC, abstractmethod
from random import randint
from typing import Iterable

import numpy as np
import inject

from fairway.domain.player import Player
from fairway.usecases.dataset import Dataset


class Simulator(ABC):

    def __init__(self, number_of_iterations: int):
        super().__init__()
        self._number_of_iterations = number_of_iterations

    @property
    def number_of_iterations(self):
        return self._number_of_iterations

    @abstractmethod
    def sample_game_scenario(self, players: Iterable[Player], number_of_holes: int) -> np.ndarray:
        pass

    @abstractmethod
    def reset(self):
        pass


class MonteCarloSimulator(Simulator):

    def __init__(self, number_of_iterations):
        super().__init__(number_of_iterations)
        self.seed = randint(0, 2**32-1)  # Generate seed

    def sample_game_scenario(self, player_handicaps: Iterable[int], number_of_holes: int) -> np.ndarray:
        """
        Returns a 2-dimensional, #players x #holes, array containing the scores of each player for each hole.
        The i-th row is associated to the i-th player
        :param player_handicaps:
        :param number_of_holes:
        :return:
        """
        dataset = inject.instance(Dataset)
        score_prob_distributions = dataset.get_score_distributions()

        n_players = len(player_handicaps)
        s = np.zeros((n_players, number_of_holes), dtype=np.int8)
        for row_index, handicap in enumerate(player_handicaps):
            distribution = score_prob_distributions.get_distribution(handicap)
            scores = np.random.choice(score_prob_distributions.score_on_the_hole, number_of_holes, p=distribution)
            np.copyto(s[row_index, :], scores)
        return s

    def reset(self):
        np.random.seed(self.seed)
