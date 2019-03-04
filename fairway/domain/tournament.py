from typing import Iterable

from fairway.domain.allowance import get_allowances
from fairway.domain.game import Game
from fairway.domain.player import Player
from fairway.domain.team import Team


class Tournament(object):
    """
    Aggregate root: contains teams, players, and game
    """
    def __init__(self, game: Game, players: Iterable[Player], number_of_teams: int, allowance_adjustment: float):
        assert isinstance(game, Game)
        assert isinstance(number_of_teams, int)
        assert (1 <= number_of_teams <= len(players))
        assert (0.0 <= allowance_adjustment <= 1.0)
        self.allowance_adjustment = allowance_adjustment
        self.game = game
        self._players = players
        self.teams = tuple(Team.create() for i in range(number_of_teams))
        allowances = get_allowances(players, self.game.number_of_holes, allowance_adjustment)
        for index, player in enumerate(self._players):
            player.allowances_by_hole = allowances[index, :]

    @property
    def players(self):
        return tuple(player for player in self._players)

    def get_team(self, team_id: int) -> Team:
        for team in self.teams:
            if team.id is team_id:
                return team

    def number_of_teams(self):
        return len(self.teams)

