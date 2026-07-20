# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import z3


def _can_be_false(A: z3.BoolRef, knowledge: z3.Solver) -> bool:
    """Check wether Not(A) is compatible with the current knowledge?"""
    knowledge.push()
    knowledge.add(z3.Not(A))
    possible = knowledge.check() == z3.sat
    knowledge.pop()
    return possible


def _can_be_true(A: z3.BoolRef, knowledge: z3.Solver) -> bool:
    """Check wether A is compatible with the current knowledge?"""
    knowledge.push()
    knowledge.add(A)
    possible = knowledge.check() == z3.sat
    knowledge.pop()
    return possible


def is_entailed(A: z3.BoolRef, K: z3.Solver) -> bool:
    """Check wether `A` is proven (ie. valid) under `K`"""
    return _can_be_true(A, K) and not _can_be_false(A, K)


def is_refuted(A: z3.BoolRef, K: z3.Solver) -> bool:
    """Check wether `A` is impossible (ie. unsatisfiable) under `K`"""
    return _can_be_false(A, K) and not _can_be_true(A, K)


def is_consistent(A: z3.BoolRef, K: z3.Solver) -> bool:
    """Check wether `A` is possible (ie. satisfiable) under `K`"""
    return _can_be_true(A, K)


def is_contingent(A: z3.BoolRef, K: z3.Solver) -> bool:
    """Check wether `A` is possible, but not guaranteed (ie. independent) under `K`"""
    return _can_be_true(A, K) and _can_be_false(A, K)


def is_irrefutable(A: z3.BoolRef, K: z3.Solver) -> bool:
    """Check wether `A` is possible, but unfalsifiable under `K`"""
    return _can_be_true(A, K) and not _can_be_false(A, K)
