# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import argparse
import logging

from icecream import ic
from rich.logging import RichHandler

import robowar


def main():
    rw = robowar.RoboWars()
    rw.log.debug("[green]Service started[/green]")
    rw.log.info("[green]Service started[/green]")
    rw.log.warning("[yellow]Cache miss[/yellow]")
    rw.log.error("[red]Connection lost[/red]")


if __name__ == "__main__":
    main()
