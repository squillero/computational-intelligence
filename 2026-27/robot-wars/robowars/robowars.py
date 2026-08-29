# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import logging

from rich.logging import RichHandler

from icecream import ic


class RoboWars:
    """Hello"""

    log: logging.Logger

    def __init__(self, log_level: logging._Level | str = "INFO"):
        ic()
        self.log = _init_log(log_level)


def _init_log(log_level) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="%X",
        handlers=[RichHandler(markup=True)],
        force=True,
    )
    logger = logging.getLogger(__name__)
    return logger
