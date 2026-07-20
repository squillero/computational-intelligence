# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import logging
import z3
from icecream import ic

NUM = 5
W = [z3.Bool(f"w_{i}") for i in range(NUM)]
S = [z3.Bool(f"s_{i}") for i in range(NUM)]


def check(solver: z3.Solver):
    for p in range(NUM):
        solver.push()
        solver.add(W[p])
        if solver.check() == z3.sat:
            logging.info(f"Satisfiability: It is possible for the Wumpus to be in {p}")
        else:
            logging.info(f"Satisfiability: It is not possible for the Wumpus to be in {p}")
        solver.pop()
    for p in range(NUM):
        solver.push()
        solver.add(z3.Not(W[p]))
        if solver.check() == z3.unsat:
            logging.info(f"Entailment: It is proven that the Wumpus is in room {p}")
        else:
            logging.info(f"Entailment: It cannot be proven that the Wumpus is in room {p}")
        solver.pop()


def main():
    solver = z3.Solver()

    solver.add(ic(S[0] == W[1]))
    solver.add(ic(S[NUM - 1] == W[NUM - 2]))
    for i in range(1, NUM - 1):
        solver.add(ic(S[i] == z3.Or(W[i - 1], W[i + 1])))

    ic(solver.assertions())

    print()
    logging.info("main: Stench, but the number of Wumpuses is uknown")
    solver.add(ic(S[1]))
    check(solver)

    print()
    logging.info('main: Adding the "Only One Wumpus" constrain')
    solver.add(ic(z3.AtMost(*W, 1)))
    check(solver)

    print()
    logging.info("main: More stench, now we can pinpoint the Wumpus")
    solver.add(ic(S[3]))
    check(solver)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    main()
# print(solver.model())
# solver.consequences
