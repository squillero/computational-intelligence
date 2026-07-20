# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import warnings
import sys

# assert not sys._is_gil_enabled(), "A free-threaded (no-GIL) Python build is required."
if sys._is_gil_enabled():
    warnings.warn(
        """
PERFORMANCE WARNING: The Global Interpreter Lock (GIL) is active.
You should use a free-threaded interpreter (eg. python3.14t)""",
        category=RuntimeWarning,
        stacklevel=2,
    )
