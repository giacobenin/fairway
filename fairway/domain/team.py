import uuid
from collections import defaultdict
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
        sorted_handicaps = sorted([int(player.handicap) for player in self._member_players])
        return "{} {} - Win Prob: {}. Expected score: {}. Handicaps: {}"\
            .format(self.__class__.__name__, self._team_id,
                    self.prob_of_winning, self.expected_score, ','.join([str(h) for h in sorted_handicaps]))

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


def create_teams_from_pre_assigned_players(players: Iterable[Player]) -> Iterable[Team]:
    # Group players by team
    players_by_team = defaultdict(list)
    for player in players:
        assert isinstance(player, Player)
        if player.team_id:
            players_by_team[player.team_id].append(player)
        else:
            assert False, "Player {} does not belong to any team".format(player.id)

    # Create teams and set members
    teams = tuple(Team.create() for i in range(len(players_by_team)))
    for team, team_members in zip(teams, players_by_team.values()):
        team.add_players(team_members)


def create_empty_teams(number_of_teams: int) -> Iterable[Team]:
    assert isinstance(number_of_teams, int)
    return tuple(Team.create() for i in range(number_of_teams))
