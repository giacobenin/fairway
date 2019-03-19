import logging
import pathlib

import inject

from fairway.app.config import create_config
from fairway.app.datasets import read_players
from fairway.domain.player import Player
from fairway.domain.team import create_empty_teams
from fairway.domain.tournament import Tournament
from fairway.usecases.bestball import BestBallGame
from fairway.usecases.interactors import create_teams


# Config
logging.basicConfig(level=logging.INFO, format='%(message)s')
project_root = pathlib.Path(__file__).parent.parent
players_file = project_root / 'data/players.csv'
score_distribution_by_handicap_file = project_root / 'data/default_usga_handicap_distributions.csv'
allowance = 1.0
number_of_best_balls = 3
number_of_teams = 4
number_of_iterations = 5000
use_swaps = True

# Prepare
inject.configure(create_config(score_distribution_by_handicap_file, number_of_iterations))
game = BestBallGame(number_of_best_balls=number_of_best_balls)
players = tuple(Player.create(player_record.handicap) for player_record in read_players(players_file))
teams = create_empty_teams(number_of_teams)
tournament = Tournament(game, players, allowance, teams)

# Execute
tournament, assignment_strategy = create_teams(tournament, use_swaps)

# Output Results
for team in tournament.teams:
    print(team)
print("Assignment Strategy: " + assignment_strategy)
