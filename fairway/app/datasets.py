from csv import reader
from collections import namedtuple
from itertools import groupby

from numpy import loadtxt

from fairway.usecases.dataset import Dataset
from fairway.usecases.distributions import ScoreDistributions


PlayerRecord = namedtuple('PlayerRecord', ['name', 'lastname', 'handicap', 'team_id'], verbose=False)
TeamRecord = namedtuple('TeamRecord', ['team_id', 'players'], verbose=False)


class CSVDataset(Dataset):

    def __init__(self, handicap_distributions_file):
        self._score_distributions = ScoreDistributions(loadtxt(fname=handicap_distributions_file, delimiter=',',
                                                               dtype=float))

    def get_score_distributions(self) -> ScoreDistributions:
        return self._score_distributions


def read_players(players_file):
    # name, lastname, handicap
    for t in _read_players(players_file, [str, str, int]):
        yield PlayerRecord(t[0], t[1], t[2], None)


def read_teams(players_file):
    # name, lastname, handicap, team_id
    teams = list()
    players = sorted(_read_players(players_file, [str, str, int, int]), key=lambda x: x[3])
    for team_id, members in groupby(players, key=lambda x: x[3]):
        teams.append(TeamRecord(team_id, tuple(PlayerRecord(m[0], m[1], m[2], m[3]) for m in members)))
    return teams


def _read_players(players_file, col_types, contains_header=False):
    """
    Generator that return PlayerRecord
    :param self:
    :param players_file:
    :return:
    """
    with open(players_file) as f:
        f_csv = reader(f)
        if contains_header:
            next(f_csv)     # Skip headers
        for row in f_csv:
            # Apply conversions to the row items
            yield tuple(convert(value) for convert, value in zip(col_types, row))
