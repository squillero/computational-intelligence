# Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import numpy as np


def f(x: np.ndarray) -> np.ndarray:
    return x[0] + x[1] / 5
