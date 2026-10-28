# Copyright © 2021 Giovanni Squillero <squillero@polito.it>
# Free for personal or classroom use; see 'LICENCE.md' for details.
# https://github.com/squillero/computational-intelligence

import argparse
import logging
from itertools import permutations, product
import numpy as np
import coloredlogs  # I like my log to be colorful
from tqdm import tqdm  # Coolest progress bar

TICTACTOE_MAP = np.array([[1, 6, 5], [8, 4, 0], [3, 2, 7]])


def display(state, legend=None, *, coordinates=False):
    if not legend:
        legend = list()
    legend += [''] * 3
    x, o = state
    for r, c in product(range(3), repeat=2):
        if TICTACTOE_MAP[r, c] in x:
            print("X", end=" ")
        elif TICTACTOE_MAP[r, c] in o:
            print("O", end=" ")
        elif coordinates:
            print(f"{TICTACTOE_MAP[r, c]}", end=" ")
        else:
            print(".", end=" ")
        if c == 2:
            print(f" {legend[r]}")


def winning_position(cells):
    return any(sum(h) == 12 for h in permutations(cells, 3))


def eval_static(state) -> int:
    """Statically evaluate a board: 1 if agent won, -1 if it lost"""
    if winning_position(state[0]):
        return 1
    elif winning_position(state[1]):
        return -1
    else:
        return 0


def next_state(state, action: int):
    """Returns the next state when agent does `action` in `state`"""
    me, opponent = state
    assert len(me) <= len(opponent)
    return frozenset(set(me) | {action}), opponent


def valid_actions(state, agent: int = 0):
    """Returns a list of valid actions"""
    if len(state[agent]) > len(state[1 - agent]):
        return list()
    else:
        return list(set(range(9)) - state[0] - state[1])


def best_action(Q: dict, state):
    if not valid_actions(state):
        return (None, eval_static(state))
    else:
        return max(((a, Q[(state, a)]) for a in valid_actions(state)), key=lambda x: x[1])


def describe_policy(Q, V):
    non_zero = [q for q in Q.items() if q[1] != 0]
    learned = [q for q in Q.items() if q[1] != 0 and q[1] != 1 and q[1] != -1]
    print(f"Found {len(non_zero):,} non zero s/a over {len(Q):,}; {len(learned):,} learned.")
    non_zero = [v for v in V.items() if v[1] != 0]
    learned = [v for v in V.items() if v[1] != 0 and v[1] != 1 and v[1] != -1]
    print(f"Found {len(non_zero):,} non zero values over {len(V):,}; {len(learned):,} learned.")


def main(train_epochs):
    states = set()
    states |= set((frozenset(x), frozenset(y)) for n in range(5) for x in permutations(range(9), n)
                  for y in permutations(set(range(9)) - set(x), n))
    states |= set((frozenset(x), frozenset(y)) for n in range(5)
                  for x in permutations(range(9), n + 1)
                  for y in permutations(set(range(9)) - set(x), n))
    states |= set((frozenset(x), frozenset(y)) for n in range(5) for x in permutations(range(9), n)
                  for y in permutations(set(range(9)) - set(x), n + 1))

    states_sorted = sorted(states, key=lambda s: len(s[0]) + len(s[1]))
    final_states = {s for s in states_sorted if len(s[0]) + len(s[1]) == 9 or eval_static(s) != 0}
    V_table = {s: eval_static(s) for s in states_sorted}
    Q_table = {(s, a): eval_static(next_state(s, a)) for s in states_sorted
               for a in valid_actions(s)}
    logging.info(f"Found {len(states):,} states, {len(final_states):,} marked as final")
    logging.info(f"V-table contains {len(V_table):,} state values")
    logging.info(f"Q-table contains {len(Q_table):,} state-action pairs (utility values)")

    # Your code here


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    parser.add_argument('-t',
                        '--train',
                        type=int,
                        metavar='EPOCH',
                        action='store',
                        dest='train_epochs',
                        help='Set random seed (default: 1_000)',
                        default=1_000)
    args = parser.parse_args()

    if args.verbose == 0:
        level = 'WARNING'
    elif args.verbose == 1:
        level = 'INFO'
    elif args.verbose == 2:
        level = 'DEBUG'
    coloredlogs.install(level=level,
                        fmt='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S')

    main(train_epochs=args.train_epochs)