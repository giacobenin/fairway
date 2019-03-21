import numpy as np
from fairway.domain.allowance import get_allowance, get_allowances
from fairway.domain.player import Player


def test_get_allowance():
    n_holes = 4
    assert [0, 0, 0, 0] == [get_allowance(hole_idx, 0, n_holes) for hole_idx in range(n_holes)]
    assert [-1, 0, 0, 0] == [get_allowance(hole_idx, 1, n_holes) for hole_idx in range(n_holes)]
    assert [-1, -1, 0, 0] == [get_allowance(hole_idx, 2, n_holes) for hole_idx in range(n_holes)]
    assert [-1, -1, -1, 0] == [get_allowance(hole_idx, 3, n_holes) for hole_idx in range(n_holes)]
    assert [-1, -1, -1, -1] == [get_allowance(hole_idx, 4, n_holes) for hole_idx in range(n_holes)]
    assert [-2, -1, -1, -1] == [get_allowance(hole_idx, 5, n_holes) for hole_idx in range(n_holes)]
    assert [-2, -2, -2, -2] == [get_allowance(hole_idx, 8, n_holes) for hole_idx in range(n_holes)]
    assert [-3, -2, -2, -2] == [get_allowance(hole_idx, 9, n_holes) for hole_idx in range(n_holes)]


def test_get_allowances():

    def test_full_handicap():
        allowance_adj = 1.0
        expected = np.array([[0, 0, 0, 0], [-1, 0, 0, 0], [-3, -2, -2, -2]])
        returned = get_allowances(players, n_holes, allowance_adj)
        np.testing.assert_array_equal(expected, returned)

    def test_no_handicap():
        allowance_adj = 0.0
        expected = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        returned = get_allowances(players, n_holes, allowance_adj)
        np.testing.assert_array_equal(expected, returned)

    # Setup
    n_holes = 4
    players = [
        Player(player_id=1, handicap_index=1),
        Player(player_id=2, handicap_index=2),
        Player(player_id=3, handicap_index=10)
    ]

    # Test
    test_full_handicap()
    test_no_handicap()
