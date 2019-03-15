import itertools
import logging
from abc import ABC, abstractmethod
from math import floor
from typing import Tuple

import inject

from fairway.domain.player import Player
from fairway.domain.tournament import Tournament
from fairway.usecases.fairness import FairnessEvaluator


class SwapGenerator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_swaps(self, tournament: Tournament):
        """

        :param tournament:
        :return: an enumeration of sorted swaps
        """
        pass


class UnfairTeamsPairsWorsePlayersOnly(ABC):

    def __init__(self, win_probability_filter: float = 0.25):
        """

        :param win_probability_filter: select only the (win_probability_filter*100)% of the players with lowest
        probability of winning
        """
        super().__init__()
        self._win_probability_filter = win_probability_filter

    def get_swaps(self, tournament: Tournament):
        players_win_prob = [player.prob_of_winning for player in tournament.players]
        k = int(floor(len(players_win_prob) * self._win_probability_filter))  # Low 25%

        swappable_players = [player for player in tournament.players if player.prob_of_winning < k]
        swaps = [players_pair for players_pair in itertools.combinations(swappable_players, 2)
                 if players_pair[0].team_id != players_pair[1].team_id]

        def swap_sorting_criteria(swap):
            player_0 = swap[0]
            player_1 = swap[1]
            team_0 = tournament.get_team(player_0.team_id)
            team_1 = tournament.get_team(player_1.team_id)
            first_key = abs(team_0.prob_of_winning - team_1.prob_of_winning)  # The wider the team win prob gap, the better
            second_key = 1.0 - (player_0.prob_of_winning - player_1.prob_of_winning)  # The closer the players win prob gap, the better
            return first_key, second_key

        swaps.sort(key=swap_sorting_criteria, reverse=True)
        return swaps


class Swapper(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def adjust_teams(self, tournament: Tournament):
        pass


class SimpleSwapper(Swapper):

    _swap_generator = inject.attr(SwapGenerator)
    _fairness_evaluator = inject.attr(FairnessEvaluator)

    def __init__(self):
        super().__init__()

    def adjust_teams(self, tournament: Tournament):
        def try_swaps():
            current_fairness = self._fairness_evaluator.get_fairness(tournament.teams)
            for players_to_swap in self._swap_generator.get_swaps(tournament):
                swap(players_to_swap, tournament)
                new_fairness = self._fairness_evaluator.get_fairness(tournament.teams)
                if new_fairness > current_fairness:
                    swap(players_to_swap)   # Not worth it, swap back
                else:
                    logging.debug("Improved fairness: {} -> {}", current_fairness, new_fairness)
                    return True     # Candidate swaps set needs to be recomputed upon player assignment changes
            return False    # No swap performed

        while not self._fairness_evaluator.is_fair_enough(tournament.teams):
            if not try_swaps():
                break   # no improving swaps were found


def swap(players_to_swap: Tuple[Player, Player], tournament: Tournament):
    team_0 = tournament.get_team(players_to_swap[0].team_id)
    team_1 = tournament.get_team(players_to_swap[1].team_id)

    team_0.remove_player(players_to_swap[0])
    team_1.remove_player(players_to_swap[1])

    team_0.add_player(players_to_swap[1])
    team_1.add_player(players_to_swap[0])
