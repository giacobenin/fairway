import numpy as np


class ScoreDistributions(object):
    """
    Class representing score distributions on a par 4 hole.
    """
    def __init__(self, handicap_distributions: np.ndarray):
        """
        Accepts a 2-dimensional array that maps the probabilities
        of scoring a hole in a certain number of attempts for each player

        Example:
                                    ATTEMPTS
                    1   2   3   4   5   6   7   8   9   10
        ---------------------------------------------------
        USGA HCP |
            0    |  0   0  0.2  ...

        Obviously, the sum of the probabilities of each row needs to sum up to 1.
        :param handicap_distributions:
        """
        assert (len(handicap_distributions.shape) == 2)

        n_handicaps, highest_score_idx = handicap_distributions.shape
        self._score_on_the_hole = tuple(i for i in range(1, highest_score_idx + 1))
        self._handicap_distributions = handicap_distributions
        # Fix possible approximation errors (row probabilities need to sum up to 1)
        for i in range(n_handicaps):
            diff = 1 - np.sum(handicap_distributions[i, :])
            if abs(diff) > 0:
                for j in range(highest_score_idx-1, 0, -1):
                    if handicap_distributions[i][j] > 0:
                        handicap_distributions[i][j] += diff
                        break

    def get_distribution(self, handicap) -> np.ndarray:
        """
        Return a 1-dimensional array representing a discrete probability distribution
        :param handicap:
        :return:
        """
        return self._handicap_distributions[handicap, :]

    @property
    def score_on_the_hole(self):
        return self._score_on_the_hole
