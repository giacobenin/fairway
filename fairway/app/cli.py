import logging

import click
import inject
from click import echo, INT, Path, IntRange

from fairway.app.config import create_config
from fairway.app.datasets import read_teams, read_players
from fairway.domain.player import Player

from fairway.usecases.interactors import estimate_teams_fairness, create_teams


@click.group()
@click.option('-i', '--iterations',
              type=IntRange(min=500, max=10000, clamp=False), default=500,
              help="the number of simulations to be performed")
@click.option('-f', '--full-handicap', 'allowance',
              type=INT, flag_value=100, default=True,
              help="Full handicap will be used to estimate the fairness of the teams")
@click.option('-n', '--no-handicap', 'allowance',
              type=INT, flag_value=0,
              help="No handicap will be used to estimate the fairness of the teams")
@click.option('-a', '--allowance', 'allowance',
              type=IntRange(min=0, max=100, clamp=False),
              help="handicap adjustment (it must be a value within 0 and 100)")
@click.option('-b', '--best-balls',
              type=IntRange(min=1, max=3, clamp=False),
              help="number of best balls")
@click.option('-d', "--distributions",
              type=Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
              help="the file containing the handicap distributions file")
@click.argument("players-file",
                type=Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True))
@click.option('-l', '--logging-level',
              type=click.Choice(['info', 'warn', 'debug']), default='warn')
@click.pass_context
def main(ctx, iterations, allowance: int, distributions: str, players_file: str, best_balls: int, logging_level):
    """
    Program to create fair Best Ball teams, evaluate their fairness, and predict their scores.
    """
    logging_opt = {
        'info': logging.INFO,
        'warn': logging.WARN,
        'debug': logging.DEBUG
    }
    logging.basicConfig(level=logging_opt[logging_level])
    ctx.obj = {
        'iterations': iterations,
        'best_balls': best_balls,
        'allowance': allowance / 100.0,     # Convert percentage to decimal value
        'distributions': distributions,
        'players_file': players_file,
        #'optimize': optimize
    }
    echo_config(iterations, allowance, distributions, players_file)
    inject.configure(create_config(distributions, iterations))


@main.command()
@click.pass_context
def estimate(ctx):
    """
    Estimate the probabilities of winning, and the expected scores, of each team
    :param ctx:
    :return:
    """
    allowance = ctx.obj['allowance']
    players_file = ctx.obj['players_file']
    best_balls = ctx.obj['best_balls']

    # Config
    players = tuple(Player.create(player_record.handicap, player_record.team_id) for team in read_teams(players_file)
                    for player_record in team.players)

    # Execute command
    tournament = estimate_teams_fairness(players, best_balls, allowance)
    echo_teams(tournament)


@main.command()
@click.option('-t', '--nteams',
              type=INT, default=2,
              help="The number of teams")
@click.option('--optimize/--no-optimize', default=False,
              help="attempts to improve the fairness of the found solution")
@click.pass_context
def assign(ctx, nteams: int, optimize: bool):
    """
    Assign the input players to the desired number of teams
    :param ctx:
    :return:
    """
    allowance = ctx.obj['allowance']
    players_file = ctx.obj['players_file']
    best_balls = ctx.obj['best_balls']

    # Config
    players = tuple(Player.create(player_record.handicap) for player_record in read_players(players_file))

    # Execute command
    tournament = create_teams(players, nteams, best_balls, allowance)
    echo_teams(tournament)


def echo_teams(tournament):
    for team in tournament.teams:
        echo("Team {}; Estimated Score: {}. Prob. of Winning: {}. Members (handicap): {}"
             .format(team.id, team.expected_score, team.prob_of_winning, [player.handicap for player in team.members]))


def echo_config(number_of_iterations, allowance, distributions, teams):
    echo("Distributions file: " + distributions)
    echo("Players file: " + teams)
    if allowance == 0:
        handicap = "no handicap"
    elif allowance == 100:
        handicap = "full_handicap"
    else:
        handicap = "handicap allowance: " + str(allowance) + "%"
    echo(handicap + " (" + str(number_of_iterations) + ")")
