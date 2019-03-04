from typing import Iterable

from numpy import floor

import numpy as np

from fairway.domain.player import Player


def get_allowances(players: Iterable[Player], number_of_holes: int, allowance_adjustment: float)-> np.ndarray:
    """
    Returns a 2-dimensional matrix with the allowances granted to each player for each hole
    :param players:
    :param number_of_holes:
    :param allowance_adjustment:
    :return:
    """
    n_players = len(players)
    handicaps = tuple(player.handicap for player in players)
    min_handicap = min(handicaps)
    allowances = np.zeros((n_players, number_of_holes))
    for index, handicap in enumerate(handicaps):
        for hole in range(number_of_holes):
            allowance = 0
            if hole <= (handicap * allowance_adjustment):
                allowance = get_allowance(hole, handicap - min_handicap, number_of_holes)
            allowances[index][hole] = allowance
    return allowances


def get_allowance(hole_idx: int, diff: int, n_holes: int) -> int:
    """
    :param hole_idx: the index of hole that is being played
    :param diff: the difference between the handicap of the current player, and the minimum handicap among all the
    players
    :param n_holes: the total number of holes of the course
    :return:
    """
    assert (0 <= hole_idx < n_holes)
    if diff <= 0:
        return 0
    hole_idx += 1
    allowance = floor(diff / n_holes)
    if hole_idx <= diff % n_holes:
        allowance += 1
    return -allowance



