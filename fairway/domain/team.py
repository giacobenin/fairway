import uuid
from typing import Iterable

from fairway.domain.player import Player
from fairway.domain.playing_entity import PlayingEntity


Team_Id = 0


class Team(PlayingEntity):

    def __init__(self, team_id: int):
        assert isinstance(team_id, int)
        self._member_players = list()
        self._team_id = team_id

    def __repr__(self):
        return "{} {} - Win Prob: {}. Expected score: {}. Handicaps: {}"\
            .format(self.__class__.__name__, self._team_id,
                    self.prob_of_winning, self.expected_score,
                    ','.join([str(player.handicap) for player in self._member_players]))

    @classmethod
    def create(cls):
        global Team_Id
        team_id = Team_Id #uuid.uuid4().int
        Team_Id += 1
        return Team(team_id)

    @property
    def id(self):
        return self._team_id

    @property
    def members(self):
        return tuple(member for member in self._member_players)

    def __lt__(self, other):
        return self.prob_of_winning < other.prob_of_winning

    def count(self):
        return len(self._member_players)

    def add_player(self, player: Player):
        self.add_players([player])

    def add_players(self, players: Iterable[Player]):
        for player in players:
            assert isinstance(player, Player)
            player.team_id = self._team_id
            self._member_players.append(player)

    def remove_player(self, player: Player):
        assert isinstance(player, Player)
        self._member_players = [member for member in self._member_players if member.id != player.id]
