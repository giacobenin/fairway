import uuid

from fairway.domain.playing_entity import PlayingEntity


Player_Id = 0


class Player(PlayingEntity):

    def __init__(self, player_id: int, handicap_index: int, team_id=None):
        assert isinstance(player_id, int)
        assert isinstance(handicap_index, int)
        assert isinstance(handicap_index, int)
        assert (0 <= handicap_index <= 36)

        self._player_id = player_id
        self._handicap = handicap_index
        self._allowances_by_hole = None
        self._team_id = team_id

    def __repr__(self):
        return "<{}: id= {} ({}), handicap:{}, win prob.:{}, expected score:{}>".format(
            self.__class__.__name__, self.id, self.team_id, self.handicap, self.prob_of_winning, self.expected_score)

    @classmethod
    def create(cls, handicap_index: int, team_id: int = None):
        global Player_Id
        player_id = Player_Id #uuid.uuid4().int
        Player_Id += 1
        player = cls(player_id, handicap_index)
        player.team_id = team_id

        return player

    @property
    def id(self):
        return self._player_id

    @property
    def team_id(self):
        return self._team_id

    @team_id.setter
    def team_id(self, team_id):
        self._team_id = team_id

    @property
    def handicap(self):
        return self._handicap

    @property
    def allowances_by_hole(self):
        return self._allowances_by_hole

    @allowances_by_hole.setter
    def allowances_by_hole(self, allowances_by_hole):
        self._allowances_by_hole = allowances_by_hole
