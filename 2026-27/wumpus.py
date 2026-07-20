# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import logging
import argparse
from itertools import product
from random import choice
import z3

from icecream import ic
import smt as k

MAP_EMPTY = "."

MAP_UNKNOWN = "?"
MAP_ME = "*"
MAP_SAFE = MAP_EMPTY
MAP_WUMPUS = "W"
MAP_MAYBE_WUMPUS = "w"
MAP_PIT = "P"
MAP_MAYBE_PIT = "p"
MAP_MAYBE_WUMPUS_OR_PIT = "!"
MAP_GOLD = "G"
MAP_MAYBE_GOLD = "g"

MAP = [".W..", "....", "...P", "..G."]
NUM_COLS = len(MAP[0])
NUM_ROWS = len(MAP)

WUMPUS = {(i, j): z3.Bool(f"wumpus_{i}_{j}") for i in range(NUM_ROWS) for j in range(NUM_COLS)}
STENCH = {(i, j): z3.Bool(f"stench_{i}_{j}") for i in range(NUM_ROWS) for j in range(NUM_COLS)}
PIT = {(i, j): z3.Bool(f"pit_{i}_{j}") for i in range(NUM_ROWS) for j in range(NUM_COLS)}
BREEZE = {(i, j): z3.Bool(f"breeze_{i}_{j}") for i in range(NUM_ROWS) for j in range(NUM_COLS)}
GOLD = {(i, j): z3.Bool(f"gold_{i}_{j}") for i in range(NUM_ROWS) for j in range(NUM_COLS)}
GLARE = {(i, j): z3.Bool(f"glare_{i}_{j}") for i in range(NUM_ROWS) for j in range(NUM_COLS)}
SAFE = {
    (i, j): z3.And(z3.Not(WUMPUS[i, j]), z3.Not(PIT[i, j]))
    for i in range(NUM_ROWS)
    for j in range(NUM_COLS)
}


def get_neighbors(pos):
    return {
        (r, pos[1]) for r in range(pos[0] - 1, pos[0] + 2) if 0 <= r < NUM_ROWS and r != pos[0]
    } | {(pos[0], c) for c in range(pos[1] - 1, pos[1] + 2) if 0 <= c < NUM_COLS and c != pos[1]}


def setup():
    solver = z3.Solver()

    # variables

    # Only one Wumpus, one pit, one gold
    ic(WUMPUS.values())
    solver.add(z3.AtMost(*WUMPUS.values(), 1))
    solver.add(z3.AtMost(*PIT.values(), 1))
    solver.add(z3.AtMost(*GOLD.values(), 1))
    solver.add(z3.AtLeast(*WUMPUS.values(), 1))
    solver.add(z3.AtLeast(*PIT.values(), 1))
    solver.add(z3.AtLeast(*GOLD.values(), 1))

    for p in product(range(NUM_ROWS), range(NUM_COLS)):
        neighbors = get_neighbors(p)
        solver.add(ic(STENCH[p] == z3.Or(WUMPUS[n] for n in neighbors)))
        solver.add(ic(BREEZE[p] == z3.Or(PIT[n] for n in neighbors)))
        solver.add(ic(GOLD[p] == z3.Or(GLARE[n] for n in neighbors)))
    exit()
    return solver


def show(model: list[list[str]]):
    for r in range(NUM_ROWS):
        print(f"{MAP[r]} | {''.join(model[r])}")
    print()


def sense(pos: tuple[int, int]) -> set[z3.BoolRef]:
    assert MAP[pos[0]][pos[1]] not in {MAP_WUMPUS, MAP_PIT}
    sensations = set()
    # Wumpus
    if any(MAP[r][c] == MAP_WUMPUS for r, c in get_neighbors(pos)):
        sensations.add(STENCH[pos])
    else:
        sensations.add(z3.Not(STENCH[pos]))
    # Pit
    if any(MAP[r][c] == MAP_PIT for r, c in get_neighbors(pos)):
        sensations.add(BREEZE[pos])
    else:
        sensations.add(z3.Not(BREEZE[pos]))
    # Gold
    if any(MAP[r][c] == MAP_GOLD for r, c in get_neighbors(pos)):
        sensations.add(GLARE[pos])
    else:
        sensations.add(z3.Not(GLARE[pos]))
    return sensations


def smt_check(
    function, fact: dict[tuple, z3.BoolRef], knowledge: z3.Solver
) -> set[tuple[int, int]]:
    ok = set()
    for p in product(range(NUM_ROWS), range(NUM_COLS)):
        if function(fact[p], knowledge):
            ok.add(p)
    return ok


def create_model(knowledge: z3.Solver) -> list[list[str]]:
    model = list()
    for _ in range(NUM_ROWS):
        model.append([MAP_UNKNOWN] * NUM_COLS)

    print(knowledge.assertions())
    exit()
    ic(k.is_consistent(WUMPUS[0, 0], knowledge))
    ic(k.is_consistent(WUMPUS[0, 1], knowledge))
    ic(k.is_consistent(WUMPUS[0, 2], knowledge))
    exit()
    ic(smt_check(k.is_consistent, WUMPUS, knowledge))
    ic(smt_check(k.is_contingent, WUMPUS, knowledge))
    ic(smt_check(k.is_entailed, WUMPUS, knowledge))
    ic(smt_check(k.is_irrefutable, WUMPUS, knowledge))
    ic(smt_check(k.is_refuted, WUMPUS, knowledge))
    exit()

    safe = smt_check(k.is_refuted, WUMPUS, knowledge) & smt_check(k.is_refuted, PIT, knowledge)
    wumpus = smt_check(k.is_entailed, WUMPUS, knowledge)
    pit = smt_check(k.is_entailed, PIT, knowledge)

    if len(wumpus) == 1:
        p = wumpus.pop()
        model[p[0]][p[1]] = MAP_WUMPUS
    if len(pit) == 1:
        p = pit.pop()
        model[p[0]][p[1]] = MAP_PIT

    for p in safe:
        model[p[0]][p[1]] = MAP_SAFE

    return model


def main():
    knowledge = setup()

    visited = set()
    safe = {(0, 0)}
    while safe:
        pos = choice(list(safe))
        ic(pos)
        visited.add(pos)
        knowledge.add(z3.Not(WUMPUS[pos]), z3.Not(PIT[pos]))

        ic(sense(pos))
        knowledge.add(sense(pos))
        model = create_model(knowledge)
        safe = {
            p
            for p in product(range(NUM_ROWS), range(NUM_COLS))
            if p not in visited and model[p[0]][p[1]] == MAP_SAFE
        }
        ic(safe)
        show(model)


if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    logging.getLogger().setLevel(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase log verbosity")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest="verbose",
        const=2,
        help="log debug messages (same as -vv)",
    )
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)

    main()
