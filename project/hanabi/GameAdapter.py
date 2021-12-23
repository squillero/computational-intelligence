import socket
import time
from typing import Tuple, Union, Dict, List

import GameData
from enum import Enum

import game


class HintType(Enum):
    NUMBER = 0
    COLOR = 1


class Color(Enum):
    UNKNOWN = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    WHITE = 5

    @staticmethod
    def fromstr(string: str):
        string = string.lower()
        dic = {"red": Color.RED, "blue": Color.BLUE, "green": Color.GREEN, "yellow": Color.YELLOW, "white": Color.WHITE}
        return dic[string]


# noinspection PyTypeChecker
class GameAdapter:
    """
    Class to play hanabi with a server.
    Use it in a for loop to iterate through the game
    """

    def __init__(self, name: str, ip: str = '127.0.0.1', port: int = 1026, datasize: int = 10240):
        """
        Initialize Game Manager creating a connection with the server
        @param name: Player Name
        @param ip: Host IP
        @param port: Process Port
        @param datasize: Size of the socket packets
        """
        self.name = name
        self.ip = ip
        self.port = port
        self.datasize = datasize
        self.move_history = []
        self.action = None
        self.game_end = False
        self.board_state = None
        self.board_state: GameData.ServerGameStateData
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.send(GameData.ClientPlayerAddData(name).serialize())
        assert type(GameData.GameData.deserialize(self.socket.recv(datasize))) is GameData.ServerPlayerConnectionOk
        print("Connection accepted by the server. Welcome " + name)
        print("[" + name + " - " + "Lobby" + "]: ", end="")
        time.sleep(1)
        self.socket.send(GameData.ClientPlayerStartRequest(name).serialize())
        data = GameData.GameData.deserialize(self.socket.recv(datasize))
        assert type(data) is GameData.ServerPlayerStartRequestAccepted
        time.sleep(0.1)
        #print("Ready: " + str(data.acceptedStartRequests) + "/" + str(data.connectedPlayers) + " players")
        data = GameData.GameData.deserialize(self.socket.recv(datasize))
        assert type(data) is GameData.ServerStartGameData
        self.socket.send(GameData.ClientPlayerReadyData(name).serialize())
        self.players = tuple(data.players)
        self.knowledge_state = {name: [(Color.UNKNOWN, 0)] * (4 if len(self.players) > 3 else 5) for name in self.players}

    def _request_state(self) -> GameData.ServerGameStateData:
        """
        Request Board State
        """
        self.socket.send(GameData.ClientGetGameStateRequest(self.name).serialize())
        while self._register_action(GameData.GameData.deserialize(self.socket.recv(self.datasize))) is not GameData.ServerGameStateData:
            if self.game_end:
                raise StopIteration

    def __iter__(self):
        """
        create iterator for proceeding through the game
        @return: self
        """
        self.current = 0
        return self

    def __next__(self) -> Tuple[GameData.ServerGameStateData, Tuple[GameData.ServerToClientData]]:
        """
        next step in the iteration
        returns the current state of the board and the list of all moves
        @rtype: board_state, move_list
        """
        if self.game_end:
            raise StopIteration

        print(f"{self.name} has requested state")
        self._request_state()
        print(f"{self.name} has recieved state")
        while self.board_state.currentPlayer != self.name:
            response = GameData.GameData.deserialize(self.socket.recv(self.datasize))
            self._register_action(response)
            self._request_state()

        return self.board_state, self.move_history

    def _send_action(self, action: GameData.ClientToServerData):
        """
        send action to the socket
        @param action: GameData
        @return: GameData
        """
        self.socket.send(action.serialize())
        response = GameData.GameData.deserialize(self.socket.recv(self.datasize))
        self._register_action(response)
        return response

    def _register_action(self, response: GameData.ServerToClientData):
        print(f"{self.name} has recieved {type(response)}")
        if type(response) is GameData.ServerGameStateData:
            response: GameData.ServerGameStateData
            self.board_state = response
            return type(response)

        elif type(response) is GameData.ServerHintData:
            response: GameData.ServerHintData
            self.move_history.append(response)
            for i in response.positions:
                known_color, known_value = self.knowledge_state[response.destination][i]
                if response.type == 'value':
                    new_know = (known_color, response.value)
                else:
                    new_know = (Color.fromstr(response.value), known_value)
                self.knowledge_state[response.destination][i] = new_know

        elif type(response) is GameData.ServerPlayerMoveOk or type(response) is GameData.ServerPlayerThunderStrike:
            response: GameData.ServerPlayerMoveOk
            self.move_history.append(response)
            position = [player.hand.index(response.card) for player in self.board_state.players if player.name == response.sender]
            if position:
                self.knowledge_state[response.player][position[0]] = (Color.UNKNOWN, 0)

        elif type(response) is GameData.ServerGameOver:
            self.game_end = True

        return type(response)

    def get_other_players(self):
        """
        Get all players but the playing one
        @return: tuple(str)
        """
        p = list(self.players)
        p.remove(self.name)
        return tuple(p)

    def send_hint(self, player: Union[str, int], type_h: HintType, val: Union[str, int]) -> bool:
        """
        Send a hint to a specific player
        @param player: player receiving the hint
        @param type_h: type of the hint to be sent
        @param val: value or colour
        @return: True if the hint was sent successfully
        """
        type_h = {HintType.NUMBER: 'value', HintType.COLOR: 'colour'}[type_h]
        result = self._send_action(GameData.ClientHintData(self.name, player, type_h, val))
        if type(result) is GameData.ServerActionInvalid:
            return False
        if type(result) is GameData.ServerHintData:
            return True
        raise ValueError

    def send_play_card(self, card_number: int) -> bool:
        """
        Play a card from hand
        @param card_number: index of the card
        @return: True if the card was correct False otherwise
        """
        result = self._send_action(GameData.ClientPlayerPlayCardRequest(self.name, card_number))
        if type(result) is GameData.ServerPlayerMoveOk:
            return True
        if type(result) is GameData.ServerPlayerThunderStrike:
            return False
        raise ValueError

    def send_discard_card(self, card_number: int) -> bool:
        """
        Discard a card
        @param card_number: card index
        @return: if the card was successfully discarded
        """
        result = self._send_action(GameData.ClientPlayerDiscardCardRequest(self.name, card_number))
        if type(result) is GameData.ServerActionValid:
            return True
        if type(result) is GameData.ServerActionInvalid:
            return False
        raise ValueError


