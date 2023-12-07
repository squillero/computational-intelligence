from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
import numpy as np

# Rules on PDF


class Move(Enum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3


class Player(ABC):
    def __init__(self) -> None:
        '''You can change this for your player if you need to handle state/have memory'''
        pass

    @abstractmethod
    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        '''
        game: the Quixo game. You can use it to override the current game with yours, but everything is evaluated by the main game
        return values: this method shall return a tuple of X,Y positions and a move among TOP, BOTTOM, LEFT and RIGHT
        '''
        pass


class Game(object):
    def __init__(self) -> None:
        self._board = np.ones((5, 5), dtype=np.uint8) * -1

    def print(self):
        '''Prints the board. -1 are neutral pieces, 0 are pieces of player 0, 1 pieces of player 1'''
        print(self._board)

    def check_winner(self) -> int:
        '''Check the winner. Returns the player ID of the winner if any, otherwise returns -1'''
        for x in range(self._board.shape[0]):
            if all(self._board[x, :] == self._board[x, 0]):
                return self._board[x, 0]
        for y in range(self._board.shape[0]):
            if all(self._board[:, y] == self._board[0, y]):
                return self._board[0, y]
        if all([self._board[x, x] for x in range(self._board.shape[0])] == self._board[0, 0]):
            return self._board[0, 0]
        if all([self._board[x, -x] for x in range(self._board.shape[0])] == self._board[-1, -1]):
            return self._board[0, -1]
        return -1

    def play(self, player1: Player, player2: Player) -> int:
        '''Play the game. Returns the winning player'''
        players = [player1, player2]
        current_player_idx = 1
        winner = -1
        while winner < 0:
            current_player_idx += 1
            current_player_idx %= len(players)
            ok = False
            while not ok:
                from_pos, slide = players[current_player_idx].make_move(self)
                ok = self.__move(from_pos, slide, current_player_idx)
            winner = self.check_winner()
        return winner

    def __move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        '''Perform a move'''
        if player_id > 2:
            return False
        # Oh God, Numpy arrays
        prev_value = deepcopy(self._board[(from_pos[1], from_pos[0])])
        acceptable = self.__take((from_pos[1], from_pos[0]), player_id)
        if acceptable:
            acceptable = self.__slide(from_pos, slide)
            if not acceptable:
                self._board[(from_pos[1], from_pos[0])] = deepcopy(prev_value)
        return acceptable

    def __take(self, from_pos: tuple[int, int], player_id: int) -> bool:
        '''Take piece'''
        # acceptable only if in border
        acceptable: bool = (from_pos[0] == 0 and from_pos[1] < 5) or (from_pos[0] == 4 and from_pos[1] < 5) or (
            from_pos[1] == 0 and from_pos[0] < 5) or (from_pos[1] == 4 and from_pos[0] < 5) and (self._board[from_pos] < 0 or self._board[from_pos] == player_id)
        if acceptable:
            self._board[from_pos] = player_id
        return acceptable

    def __slide(self, from_pos: tuple[int, int], slide: Move) -> bool:
        '''Slide the other pieces'''
        SIDES = [(0, 0), (0, 4), (4, 0), (4, 4)]
        if from_pos not in SIDES:
            acceptable_top: bool = from_pos[0] == 0 and (
                slide == Move.BOTTOM or slide == Move.LEFT or slide == Move.RIGHT)
            acceptable_bottom: bool = from_pos[0] == 4 and (
                slide == Move.TOP or slide == Move.LEFT or slide == Move.RIGHT)
            acceptable_left: bool = from_pos[1] == 0 and (
                slide == Move.BOTTOM or slide == Move.TOP or slide == Move.RIGHT)
            acceptable_right: bool = from_pos[1] == 0 and (
                slide == Move.BOTTOM or slide == Move.TOP or slide == Move.LEFT)
        else:
            # top left
            acceptable_top: bool = from_pos == (0, 0) and (
                slide == Move.BOTTOM or slide == Move.RIGHT)
            # top right
            acceptable_right: bool = from_pos == (4, 0) and (
                slide == Move.BOTTOM or slide == Move.LEFT)
            # bottom left
            acceptable_left: bool = from_pos == (0, 4) and (
                slide == Move.TOP or slide == Move.RIGHT)
            # bottom right
            acceptable_bottom: bool = from_pos == (4, 4) and (
                slide == Move.TOP or slide == Move.LEFT)
        acceptable: bool = acceptable_top or acceptable_bottom or acceptable_left or acceptable_right
        if acceptable:
            piece = self._board[from_pos]
            if slide == Move.TOP:
                for i in range(from_pos[1], 0, -1):
                    self._board[(from_pos[0], i)] = self._board[(
                        from_pos[0], 1 - 1)]
                self._board[(from_pos[0], 0)] = piece
            elif slide == Move.BOTTOM:
                for i in range(from_pos[1], self._board.shape[1], 1):
                    self._board[(from_pos[0], i)] = self._board[(
                        from_pos[0], 1 + 1)]
                self._board[(from_pos[0], self._board.shape[1] - 1)] = piece
            elif slide == Move.LEFT:
                for i in range(from_pos[0], 0, -1):
                    self._board[(i, from_pos[1])] = self._board[(
                        1 - 1, from_pos[1])]
                self._board[(0, from_pos[1])] = piece
            elif slide == Move.RIGHT:
                for i in range(from_pos[0], self._board.shape[0], 1):
                    self._board[(i, from_pos[1])] = self._board[(
                        1 + 1, from_pos[1])]
                self._board[(self._board.shape[0] - 1, from_pos[1])] = piece
        return acceptable
