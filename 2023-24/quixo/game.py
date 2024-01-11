from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
import numpy as np

# Rules on PDF and https://cdn.1j1ju.com/medias/a8/5e/26-quixo-rulebook.pdf


class Move(Enum):
    '''
    Selects where you want to place the taken piece. The rest of the pieces are shifted
    '''
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
        The game accepts coordinates of the type (X, Y). X goes from left to right, while Y goes from top to bottom, as in 2D graphics.
        Thus, the coordinates that this method returns shall be in the (X, Y) format.

        game: the Quixo game. You can use it to override the current game with yours, but everything is evaluated by the main game
        return values: this method shall return a tuple of X,Y positions and a move among TOP, BOTTOM, LEFT and RIGHT
        '''
        pass


class Game(object):
    def __init__(self) -> None:
        self._board = np.full((5, 5), -1, dtype=np.int8)
        self.current_player_idx = 1

    def get_board(self) -> np.ndarray:
        '''
        Returns the board
        '''
        return deepcopy(self._board)

    def get_current_player(self) -> int:
        '''
        Returns the current player
        '''
        return deepcopy(self.current_player_idx)

    def print(self):
        '''Prints the board. -1 are neutral pieces, 0 are pieces of player 0, 1 pieces of player 1'''
        print(self._board)

    def check_winner(self) -> int:
        '''Check the winner. Returns the player ID of the winner if any, otherwise returns -1'''
        # for each row
        player = self.get_current_player()
        winner = -1
        for x in range(self._board.shape[0]):
            # if a player has completed an entire row
            if self._board[x, 0] != -1 and all(self._board[x, :] == self._board[x, 0]):
                # return winner is this guy
                winner = self._board[x, 0]
        if winner > -1 and winner != self.get_current_player():
            return winner
        # for each column
        for y in range(self._board.shape[1]):
            # if a player has completed an entire column
            if self._board[0, y] != -1 and all(self._board[:, y] == self._board[0, y]):
                # return the relative id
                winner = self._board[0, y]
        if winner > -1 and winner != self.get_current_player():
            return winner
        # if a player has completed the principal diagonal
        if self._board[0, 0] != -1 and all(
            [self._board[x, x]
                for x in range(self._board.shape[0])] == self._board[0, 0]
        ):
            # return the relative id
            winner = self._board[0, 0]
        if winner > -1 and winner != self.get_current_player():
            return winner
        # if a player has completed the secondary diagonal
        if self._board[0, -1] != -1 and all(
            [self._board[x, -(x + 1)]
             for x in range(self._board.shape[0])] == self._board[0, -1]
        ):
            # return the relative id
            winner = self._board[0, -1]
        return winner

    def play(self, player1: Player, player2: Player) -> int:
        '''Play the game. Returns the winning player'''
        players = [player1, player2]
        winner = -1
        while winner < 0:
            self.current_player_idx += 1
            self.current_player_idx %= len(players)
            ok = False
            while not ok:
                from_pos, slide = players[self.current_player_idx].make_move(
                    self)
                ok = self.__move(from_pos, slide, self.current_player_idx)
            winner = self.check_winner()
        return winner

    def __move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        '''Perform a move'''
        if player_id not in (0, 1):
            return False
        prev_value = deepcopy(self._board[(from_pos[1], from_pos[0])])
        acceptable = self.__take((from_pos[1], from_pos[0]), player_id)
        if acceptable:
            acceptable = self.__slide((from_pos[1], from_pos[0]), slide)
            if not acceptable:  # restore previous
                self._board[(from_pos[1], from_pos[0])] = deepcopy(prev_value)
        return acceptable

    def __take(self, from_pos: tuple[int, int], player_id: int) -> bool:
        """Checks that {from_pos} is in the border and marks the cell with {player_id}"""
        row, col = from_pos
        from_border = row in (0, 4) or col in (0, 4)
        if not from_border:
            return False  # the cell is not in the border
        if self._board[from_pos] != player_id and self._board[from_pos] != -1:
            return False  # the cell belongs to the opponent
        self._board[from_pos] = player_id
        return True

    @staticmethod
    def __acceptable_slides(from_position: tuple[int, int]):
        """When taking a piece from {from_position} returns the possible moves (slides)"""
        acceptable_slides = [Move.BOTTOM, Move.TOP, Move.LEFT, Move.RIGHT]
        axis_0 = from_position[0]    # axis_0 = 0 means uppermost row
        axis_1 = from_position[1]    # axis_1 = 0 means leftmost column

        if axis_0 == 0:  # can't move upwards if in the top row...
            acceptable_slides.remove(Move.TOP)
        elif axis_0 == 4:
            acceptable_slides.remove(Move.BOTTOM)

        if axis_1 == 0:
            acceptable_slides.remove(Move.LEFT)
        elif axis_1 == 4:
            acceptable_slides.remove(Move.RIGHT)
        return acceptable_slides

    def __slide(self, from_pos: tuple[int, int], slide: Move) -> bool:
        '''Slide the other pieces'''
        if slide not in self.__acceptable_slides(from_pos):
            return False  # consider raise ValueError('Invalid argument value')
        axis_0, axis_1 = from_pos
        # np.roll performs a rotation of the element of a 1D ndarray
        if slide == Move.RIGHT:
            self._board[axis_0] = np.roll(self._board[axis_0], -1)
        elif slide == Move.LEFT:
            self._board[axis_0] = np.roll(self._board[axis_0], 1)
        elif slide == Move.BOTTOM:
            self._board[:, axis_1] = np.roll(self._board[:, axis_1], -1)
        elif slide == Move.TOP:
            self._board[:, axis_1] = np.roll(self._board[:, axis_1], 1)
        return True
