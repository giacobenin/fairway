from abc import ABC, abstractmethod
from fairway.usecases.distributions import ScoreDistributions


class Dataset(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_score_distributions(self)-> ScoreDistributions:
        pass
