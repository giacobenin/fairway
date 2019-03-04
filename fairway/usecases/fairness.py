from abc import ABC, abstractmethod
from typing import Iterable

from fairway.domain.team import Team


class FairnessEvaluator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_fairness(self, teams: Iterable[Team]) -> float:
        pass

    @property
    @abstractmethod
    def tolerance(self) -> float:
        pass

    @abstractmethod
    def is_fair_enough(self,teams: Iterable[Team]) -> bool:
        pass


class MaxDifference(FairnessEvaluator):

    def __init__(self, tolerance):
        super().__init__()
        self._tolerance = tolerance

    def get_fairness(self, teams: Iterable[Team]) -> float:
        sorted_teams = sorted(teams)
        return sorted_teams[-1].prob_of_winning - sorted_teams[0].prob_of_winning

    @property
    def tolerance(self) -> float:
        return self._tolerance

    def is_fair_enough(self, teams: Iterable[Team]) -> bool:
        self.get_fairness(teams) < self.tolerance