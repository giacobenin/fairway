import logging
from collections import defaultdict
from sys import float_info
from typing import Iterable

import inject

from fairway.domain.player import Player
from fairway.domain.tournament import Tournament
from fairway.usecases.assignment import ABCDByHandicap, ABCDByWinProbability, ZigZagByHandicap, \
    ZigZagByWinProbability, WeakestFirstByHandicap, WeakestFirstByWinProbability
from fairway.usecases.bestball import BestBallGame
from fairway.usecases.fairness import FairnessEvaluator
from fairway.usecases.swaps import Swapper


def estimate_teams_fairness(players: Iterable[Player], number_of_best_balls: int, allowance_adjustment: float) -> Tournament:
    """
    Simulate a game where players play in teams
    :param players:
    :param number_of_best_balls:
    :param allowance_adjustment:
    :return:
    """
    # Group players by team
    players_by_team = defaultdict(list)
    for player in players:
        players_by_team[player.team_id].append(player)

    # Create tournament
    game = BestBallGame(number_of_best_balls=number_of_best_balls)
    tournament = Tournament(game, players, len(players_by_team), allowance_adjustment)
    for team, team_members in zip(tournament.teams, players_by_team.values()):
        team.add_players(team_members)

    # Play game
    game.play_team_game(tournament.players, tournament.teams)

    return tournament


def create_teams(players: Iterable[Player], number_of_teams: int, number_of_best_balls: int, allowance_adjustment: float, optimize: bool) -> Tournament:

    for player in players:
        assert (player.team_id is None)

    fairness_evaluator = inject.instance(FairnessEvaluator)
    game = BestBallGame(number_of_best_balls=number_of_best_balls)
    tournament = Tournament(game, players, number_of_teams, allowance_adjustment)

    # Play individual game
    game.play_individual_game(players)

    for player in players:
        print(player)

    # Assign players to teams
    assignment_strategies = [
        ABCDByHandicap(), ABCDByWinProbability(),
        ZigZagByHandicap(), ZigZagByWinProbability(),
        WeakestFirstByHandicap(), WeakestFirstByWinProbability()
    ]

    fairest_assignment = None
    fairest_tournament = None
    fairness = float_info.max
    for strategy in assignment_strategies:
        tournament = Tournament(game, players, number_of_teams, allowance_adjustment)
        strategy.assign_players_to_teams(players, tournament.teams)
        tournament = estimate_teams_fairness(players, number_of_best_balls, allowance_adjustment)
        current_fairness = fairness_evaluator.get_fairness(tournament.teams)
        logging.info("Strategy: {} Fairness: {}\tTeams: {}".
                     format(strategy.__class__.__name__, current_fairness, tournament.teams))
        if current_fairness < fairness:
            # Pick the fairest of all the assignments
            fairness = current_fairness
            fairest_tournament = tournament
            fairest_assignment = {player.id: player.team_id for player in players}  # Remember the assignment

    # Re-apply the fairest assignment
    for player in players:
        player.team_id = fairest_assignment[player.id]

    # Try to improve the fairest assignment
    if optimize:
        swapper = inject.instance(Swapper)
        swapper.adjust_teams(fairest_tournament)

    return tournament

