# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import logging
import argparse
from itertools import product
import z3

from icecream import ic

solver = z3.Solver()
A = z3.Bool("A")
B = z3.Bool("B")
C = z3.Bool("C")

solver.add(A == z3.Or(B, C))
solver.add(z3.Not(A))

solver.add(B)
ic(solver.assertions())
ic(solver.check())
