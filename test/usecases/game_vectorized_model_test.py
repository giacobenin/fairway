from fairway.domain.player import Player
from fairway.domain.team import Team
from fairway.usecases.bestball import GameVectorizedModel

players = [
    Player(player_id=0, handicap_index=6, team_id=1),
    Player(player_id=1, handicap_index=7, team_id=2),
    Player(player_id=2, handicap_index=5, team_id=3),

    Player(player_id=3, handicap_index=4, team_id=1),
    Player(player_id=4, handicap_index=1, team_id=2),
    Player(player_id=5, handicap_index=1, team_id=3),

    Player(player_id=6, handicap_index=1, team_id=1),
    Player(player_id=7, handicap_index=17, team_id=2),
    Player(player_id=8, handicap_index=9, team_id=3)
]


def test_players_by_team():
    model = GameVectorizedModel(players)

    for player in model.players_by_team[0:3]:
        assert player.team_id == 1

    for player in model.players_by_team[3:6]:
        assert player.team_id == 2

    for player in model.players_by_team[6:9]:
        assert player.team_id == 3


def test_handicaps():
    model = GameVectorizedModel(players)

    for handicaps in zip(sorted([player.handicap for player in model.players_by_team[0:3]]), (1, 4, 6)):
        assert handicaps[0] == handicaps[1]

    for handicaps in zip(sorted([player.handicap for player in model.players_by_team[3:6]]), (1, 7, 17)):
        assert handicaps[0] == handicaps[1]

    for handicaps in zip(sorted([player.handicap for player in model.players_by_team[6:9]]), (1, 5, 9)):
        assert handicaps[0] == handicaps[1]


def test_teams():
    teams = [Team(team_id=1), Team(team_id=2), Team(team_id=3)]

    teams[0].add_players([player for player in players if player.team_id == teams[0].id])
    teams[1].add_players([player for player in players if player.team_id == teams[1].id])
    teams[2].add_players([player for player in players if player.team_id == teams[2].id])

    model = GameVectorizedModel(players, teams)

    assert model.teams[0][0] == 0
    assert model.teams[0][1] == 1
    assert model.teams[0][-1] == 2

    assert model.teams[1][0] == 3
    assert model.teams[1][1] == 4
    assert model.teams[1][-1] == 5

    assert model.teams[2][0] == 6
    assert model.teams[2][1] == 7
    assert model.teams[2][-1] == 8
