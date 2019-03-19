from typing import Iterable

from fairway.domain.allowance import get_allowances
from fairway.domain.game import Game
from fairway.domain.player import Player
from fairway.domain.team import Team


class Tournament(object):
    """
    Aggregate root: contains game, players, and teams (if not an individual game)
    """
    def __init__(self, game: Game, players: Iterable[Player], allowance_adjustment: float, teams: Iterable[Team] = None):
        assert isinstance(game, Game)
        if teams:
            assert (1 <= len(teams) <= len(players))
        assert (0.0 <= allowance_adjustment <= 1.0)
        self.allowance_adjustment = allowance_adjustment
        self.game = game
        self._players = players
        self.teams = teams
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
