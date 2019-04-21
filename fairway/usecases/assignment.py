import itertools
from collections import deque
from heapq import heappush, heappop
from math import floor

from fairway.domain.player import Player
from fairway.domain.team import Team


class AssignmentStrategy(object):

    def __init__(self, player_goodness_criteria, assignment_strategy):
        super().__init__()
        self.player_goodness_criteria = player_goodness_criteria
        self.assignment_strategy = assignment_strategy

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

    def assign_players_to_teams(self, players, teams):
        players_per_team = floor(len(players) / len(teams))
        larger_teams = len(players) % len(teams)   # If the number of teams is not a divisor of the number of players...
        sorted_players = deque(sorted(players, key=self.player_goodness_criteria, reverse=True))

        for team in teams:
            team.reset()

        for team in self.assignment_strategy(teams, self.player_goodness_criteria):
            if len(sorted_players) <= 0:
                break
            if len(team.members) > players_per_team:
                if larger_teams > 0 and len(team.members) < (players_per_team+1):
                    team.add_player(sorted_players.popleft())
                    larger_teams -= 1
                else:
                    continue
            else:
                team.add_player(sorted_players.popleft())


# Strategies

class ABCDByHandicap(AssignmentStrategy):

    def __init__(self):
        super().__init__(goodness_hcp, abcd)


class ABCDByWinProbability(AssignmentStrategy):

    def __init__(self):
        super().__init__(goodness_win_prob, abcd)


class ZigZagByHandicap(AssignmentStrategy):

    def __init__(self):
        super().__init__(goodness_hcp, zig_zag)


class ZigZagByWinProbability(AssignmentStrategy):

    def __init__(self):
        super().__init__(goodness_win_prob, zig_zag)


class WeakestFirstByHandicap(AssignmentStrategy):

    def __init__(self):
        super().__init__(goodness_hcp, weakest_first)


class WeakestFirstByWinProbability(AssignmentStrategy):

    def __init__(self):
        super().__init__(goodness_win_prob, weakest_first)


class WeakestFirstByWinProbabilityByHole(AssignmentStrategy):

    def __init__(self, hole_index):
        super().__init__(GoodnessWinProbByHole(hole_index).goodness, weakest_first)
        self._hole_index = hole_index

    def __repr__(self):
        return "{}-{}".format(self.__class__.__name__, self._hole_index)

# Functions to evaluate the goodness of a player, or of a team


def goodness_hcp(player):
    assert isinstance(player, Player)
    return player.handicap


def goodness_win_prob(player):
    assert isinstance(player, Player)
    return player.metrics.win_prob


class GoodnessWinProbByHole:

    def __init__(self, hole_index):
        self._hole_index = hole_index

    def goodness(self, player):
        assert isinstance(player, Player)
        return player.metrics.win_prob_by_hole[self._hole_index]


def goodness(team, player_goodness_criteria):
    assert isinstance(team, Team)
    return sum(player_goodness_criteria(member) for member in team.members)


# Assignment strategies


def abcd(teams, _):
    for team in itertools.cycle(teams):
        yield team


def zig_zag(teams, _):
    for team in itertools.cycle(teams+tuple(t for t in reversed(teams))):
        yield team


def weakest_first(teams, player_goodness_criteria):
    sorted_team_wrappers = sorted([(0, team) for team in teams])
    teams_q = []  # Min heap
    for team_wrapper in sorted_team_wrappers:
        heappush(teams_q, team_wrapper)
    while len(sorted_team_wrappers) > 0:
        team_wrapper = heappop(teams_q)   # Pop weakest team
        yield team_wrapper[1]
        team_wrapper = (goodness(team_wrapper[1], player_goodness_criteria), team_wrapper[1])
        heappush(teams_q, team_wrapper)     # Push it back
