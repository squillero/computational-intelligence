# Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import numpy as np

# All numpy's mathematical functions can be used in formulas
# see: https://numpy.org/doc/stable/reference/routines.math.html


# Notez bien: No need to include f0 -- it's just an example!
def f0(x: np.ndarray) -> np.ndarray:
    return x[0] + np.sin(x[1]) / 5


def f1(x: np.ndarray) -> np.ndarray: ...


def f2(x: np.ndarray) -> np.ndarray: ...


def f3(x: np.ndarray) -> np.ndarray: ...


def f4(x: np.ndarray) -> np.ndarray: ...


def f5(x: np.ndarray) -> np.ndarray: ...


def f6(x: np.ndarray) -> np.ndarray: ...


def f7(x: np.ndarray) -> np.ndarray: ...


def f8(x: np.ndarray) -> np.ndarray: ...
