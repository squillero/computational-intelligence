import socket
import time
import typing

import GameData
from enum import Enum


class HintType(Enum):
    NUMBER = 0
    COLOR = 1


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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.send(GameData.ClientPlayerAddData(name).serialize())
        self.response_list = []
        assert type(GameData.GameData.deserialize(self.socket.recv(datasize))) is GameData.ServerPlayerConnectionOk
        print("Connection accepted by the server. Welcome " + name)
        print("[" + name + " - " + "Lobby" + "]: ", end="")
        input("START?")
        self.socket.send(GameData.ClientPlayerStartRequest(name).serialize())
        data = GameData.GameData.deserialize(self.socket.recv(datasize))
        assert type(data) is GameData.ServerPlayerStartRequestAccepted
        time.sleep(0.1)
        print("Ready: " + str(data.acceptedStartRequests) + "/" + str(data.connectedPlayers) + " players")
        data = GameData.GameData.deserialize(self.socket.recv(datasize))
        assert type(data) is GameData.ServerStartGameData
        print("Game Start!")
        self.socket.send(GameData.ClientPlayerReadyData(name).serialize())
        self.board_state = self.__request_state()
        self.players = tuple(data.players)

    def __request_state(self) -> GameData.ServerGameStateData:
        """
        Request Board State
        @return: Board State
        """
        self.socket.send(GameData.ClientGetGameStateRequest(self.name).serialize())
        while True:
            b_state = GameData.GameData.deserialize(self.socket.recv(self.datasize))
            if type(b_state) is not GameData.ServerGameStateData:
                self.move_history += (b_state,)
            else:
                break
        return b_state

    def __iter__(self):
        """
        create iterator for proceeding through the game
        @return: self
        """
        self.current = 0
        self.move_history = ()
        self.action = None
        self.board_state = None
        return self

    def __next__(self):
        """
        next step in the iteration
        returns the current state of the board and the list of all moves
        @rtype: board_state, move_list
        """
        self.board_state = self.__request_state()
        while self.board_state.currentPlayer != self.name:
            response = GameData.GameData.deserialize(self.socket.recv(self.datasize))
            if type(response) is GameData.ServerGameOver:
                raise StopIteration
            self.move_history += (response,)
            self.board_state = self.__request_state()

        return self.board_state, self.move_history

    def __send_action(self, action: GameData.ClientToServerData):
        """
        send action to the socket
        @param action: GameData
        @return: GameData
        """
        self.socket.send(action.serialize())
        response = GameData.GameData.deserialize(self.socket.recv(self.datasize))
        self.move_history += (response,)
        return response

    def get_other_players(self):
        """
        Get all players but the playing one
        @return: tuple(str)
        """
        p = list(self.players)
        p.remove(self.name)
        return tuple(p)

    def send_hint(self, player: typing.Union[str, int], type_h: HintType, val: typing.Union[str, int]) -> bool:
        """
        Send a hint to a specific player
        @param player: player receiving the hint
        @param type_h: type of the hint to be sent
        @param val: value or colour
        @return: True if the hint was sent successfully
        """
        type_h = {HintType.NUMBER: 'value', HintType.COLOR: 'colour'}[type_h]
        result = self.__send_action(GameData.ClientHintData(self.name, player, type_h, val))
        if type(result) is GameData.ServerActionInvalid:
            return False
        if type(result) is GameData.ServerHintData:
            return True
        raise ValueError

    def play_card(self, card_number: int) -> bool:
        """
        Play a card from hand
        @param card_number: index of the card
        @return: True if the card was correct False otherwise
        """
        result = self.__send_action(GameData.ClientPlayerPlayCardRequest(self.name, card_number))
        if type(result) is GameData.ServerPlayerMoveOk:
            return True
        if type(result) is GameData.ServerPlayerThunderStrike:
            return False
        raise ValueError

    def discard_card(self, card_number: int) -> bool:
        """
        Discard a card
        @param card_number: card index
        @return: if the card was successfully discarded
        """
        result = self.__send_action(GameData.ClientPlayerDiscardCardRequest(self.name, card_number))
        if type(result) is GameData.ServerActionValid:
            return True
        if type(result) is GameData.ServerActionInvalid:
            return False
        raise ValueError
