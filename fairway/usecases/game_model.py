from numpy import vstack


class GameVectorizedModel:
    """
    Vectorized representation of players, teams, and their properties
    """
    def __init__(self, players, teams=None):
        # 1. Sort players by teams (simplifies slicing by group)
        self._player_id_to_index = dict()
        self._players_by_team = sorted(players, key=lambda p: p.team_id) if teams else players
        for index, player in enumerate(self._players_by_team):
            self._player_id_to_index[player.id] = index

        # 2. Compute vector containing handicap of all players
        self._player_handicaps = tuple(player.handicap for player in self._players_by_team)

        # 3. Compute nPlayers x nHoles matrix containing the allowances granted to each player for each hole
        self._allowances = vstack((player.allowances_by_hole for player in self._players_by_team))

        # 4.
        # Create list of tuples, each of them containing the indexes of its members
        self._team_id_to_index = dict()
        self._teams_as_player_indexes = list()
        if teams:
            for index, team in enumerate(teams):
                self._teams_as_player_indexes.append(list(self.player_id_to_index[player.id] for player in team.members))
                self._team_id_to_index[team.id] = index
            self._teams_as_player_indexes = [sorted(t) for t in self._teams_as_player_indexes]

    @property
    def player_id_to_index(self):
        return self._player_id_to_index

    @property
    def team_id_to_index(self):
        return self._team_id_to_index

    @property
    def players_by_team(self):
        """
        :return: vector containing all players, sorted by team so that players that belong to the same team are
                next to each other
        """
        return self._players_by_team

    @property
    def handicaps(self):
        """
        :return: vector containing the handicap of all the players. The i-th element is the  handicap of the i-th
                 player in players_by_team
        """
        return self._player_handicaps

    @property
    def allowances(self):
        """
        :return: nPlayer x nHole matrix, where each cell represent the allowances granted to the i-th player
                 at the j-th hole
        """
        return self._allowances

    @property
    def teams(self):
        """
        :return: a list of lists. Each list element contains players_by_team's indexes of the team members. The indexes
                 are sorted
        """
        return self._teams_as_player_indexes

