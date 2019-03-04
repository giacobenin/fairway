from abc import ABC, abstractmethod


class Game(ABC):

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def number_of_holes(self) -> float:
        pass

    @abstractmethod
    def play_individual_game(self, players):
        pass

    @abstractmethod
    def play_team_game(self, players, teams):
        pass
