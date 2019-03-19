from abc import ABC, abstractmethod


class PlayingEntity(ABC):

    def __init__(self, expected_score=0.0, prob_of_winning=0.0):
        self._expected_score = expected_score
        self._prob_of_winning = prob_of_winning

    @property
    def expected_score(self):
        return self._expected_score

    @expected_score.setter
    def expected_score(self, score):
        self._expected_score = score

    @property
    def prob_of_winning(self):
        return self._prob_of_winning

    @prob_of_winning.setter
    def prob_of_winning(self, score):
        self._prob_of_winning = score

    def reset(self):
        self._expected_score = 0.0
        self._prob_of_winning = 0.0
