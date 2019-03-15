import logging
import pathlib

import inject

from fairway.app.config import create_config
from fairway.app.datasets import read_players
from fairway.domain.player import Player
from fairway.usecases.interactors import create_teams


# Config
logging.basicConfig(level=logging.DEBUG)
project_root = pathlib.Path(__file__).parent.parent
players_file = project_root / 'data/players.csv'
score_distribution_by_handicap_file = project_root / 'data/default_usga_handicap_distributions.csv'
allowance = 1.0
number_of_best_balls = 2
number_of_teams = 4
number_of_iterations = 500
use_swaps = True
inject.configure(create_config(score_distribution_by_handicap_file, number_of_iterations))

# Execute
players = tuple(Player.create(player_record.handicap) for player_record in read_players(players_file))
tournament = create_teams(players, number_of_teams, number_of_best_balls, allowance, use_swaps)

# Output Results
for team in tournament.teams:
    print("Team {}; Estimated Score: {}. Prob. of Winning: {}. Members: {}".
          format(team.id, team.expected_score, team.prob_of_winning, [player.handicap for player in team.members]))
