import logging
from copy import deepcopy
from sys import float_info

import inject

from fairway.domain.team import Team
from fairway.domain.tournament import Tournament
from fairway.usecases.assignment import ABCDByHandicap, ABCDByWinProbability, ZigZagByHandicap, \
    ZigZagByWinProbability, WeakestFirstByHandicap, WeakestFirstByWinProbability
from fairway.usecases.fairness import FairnessEvaluator
from fairway.usecases.swaps import Swapper


def create_teams(tournament: Tournament, optimize: bool) -> (Tournament, str):
    """

    :param tournament:
    :param optimize:
    :return: the fairest team that could be found, along with the assignment heuristic that was used to find it
    """

    # Play individual game
    tournament.game.play_individual_game(tournament.players)
    for player in tournament.players:
        logging.info("{}".format(player))

    # Assign players to teams
    assignment_strategies = [
        ABCDByHandicap(), ABCDByWinProbability(),
        ZigZagByHandicap(), ZigZagByWinProbability(),
        WeakestFirstByHandicap(), WeakestFirstByWinProbability()
    ]

    fairness_evaluator = inject.instance(FairnessEvaluator)
    fairest_assignment = None
    fairness = float_info.max
    for strategy in assignment_strategies:
        curr_players = tuple(deepcopy(p) for p in tournament.players)
        curr_teams = tuple(Team(t.id) for t in tournament.teams)
        strategy.assign_players_to_teams(curr_players, curr_teams)
        tournament.game.play_team_game(curr_players, curr_teams)
        current_fairness = fairness_evaluator.get_fairness(curr_teams)
        logging.info("Strategy: {} Fairness: {}\nTeams: {}".
                     format(strategy.__class__.__name__, current_fairness, curr_teams))
        if current_fairness < fairness:
            # Pick the fairest of all the assignments
            fairness = current_fairness
            fairest_assignment = (curr_players, curr_teams, strategy.__class__.__name__)

    tournament = Tournament(tournament.game, fairest_assignment[0], tournament.allowance_adjustment, fairest_assignment[1])

    # Try to improve the fairest assignment
    if optimize:
        swapper = inject.instance(Swapper)
        swapper.adjust_teams(tournament)

    return tournament, fairest_assignment[2]


def estimate_teams_fairness(tournament: Tournament) -> Tournament:
    tournament = Tournament(tournament.game, tournament.players, tournament.allowance_adjustment, tournament.teams)
    tournament.game.play_team_game(tournament.players, tournament.teams)
    return tournament

