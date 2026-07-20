# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

import sys
import logging
import argparse
import threading
import time

import arcade
from icecream import ic


class RobotBrain(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name = name
        # Thread-safe raw variables
        self.x = 100
        self.y = 100

    def run(self):
        """This runs on its own core in parallel!"""
        while True:
            # Complex AI calculation (e.g., pathfinding) happens here
            time.sleep(0.5)
            self.x += 10  # Safely modify coordinates


class RobowarsGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Robowars")
        # Start the robot thread
        self.bot_brain = RobotBrain("Striker")
        self.bot_brain.start()

        # Create the visual sprite on the MAIN thread
        self.bot_sprite = arcade.SpriteSolidColor(30, 30, arcade.color.RED)

    def on_update(self, delta_time):
        # Sync the visual sprite to the background thread's calculated position
        self.bot_sprite.center_x = self.bot_brain.x
        self.bot_sprite.center_y = self.bot_brain.y

    def on_draw(self):
        self.clear()


def main():
    ic()
    game = RobowarsGame()
    arcade.run()


if __name__ == "__main__":
    assert not sys._is_gil_enabled(), "A free-threaded (no-GIL) Python build is required."

    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    logging.getLogger().setLevel(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase log verbosity")
    parser.add_argument(
        "-d", "--debug", action="store_const", dest="verbose", const=2, help="log debug messages (same as -vv)"
    )
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)

    main()
