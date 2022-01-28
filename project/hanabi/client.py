#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread
import GameData
import socket
from constants import *
import os

CLIENT_STATUSES = ["Lobby", "Game", "GameHint"]

CLIENT_MOVES = ["hint", "play", "discard"]

CARD_COLORS = ["green", "red", "blue", "yellow", "white"]

class Client:
    def __init__(self, playerName, ip, port):
        self.playerName = playerName
        self.ip = ip
        self.port = port
        self.hintState = ("", "")
        self.run = True
        self.status = CLIENT_STATUSES[0]
        self.move_history = []
        self.all_players_ready = False
        self.game_data_copy = {'player': None, 'usedStormTokens': 0, 'usedNoteTokens': 0}
        pass

    def start(self):
        print("Client::start - base class stub")
        pass

    def record_move(self, move, outcome):
        # TO-DO: always call this fn on every move
        # TO-DO:  decide representation for outcome; calculate before calling this fn
        self.move_history.append((move, outcome))

    def build_hint_command(self, _type, _dest, _payload):
        # in the form of:
        # hint color <dest> <color in CARD_COLORS>,  or:
        # hint value <dest> <value in 1-5>
        return f"hint {_type} {_dest} {_payload}"

    def build_discard_command(self, idx):
        return f"discard {idx % 5}"  # force idx bounds-safety

    def build_play_command(self, idx):
        return f"play {idx % 5}"  # force idx bounds-safety

    def begin_socket_connection(self, s):
        request = GameData.ClientPlayerAddData(self.playerName)
        s.connect((self.ip, self.port))
        s.send(request.serialize())
        data = s.recv(DATASIZE)
        data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerPlayerConnectionOk:
            print("Connection accepted by the server. Welcome " + self.playerName)
        print("[" + self.playerName + " - " + self.status + "]: ", end="")

    def process_incoming_data(self, data, s):
        dataOk = False

        if type(data) is GameData.ServerPlayerStartRequestAccepted:
            dataOk = True
            print("Ready: " + str(data.acceptedStartRequests) + "/" + str(data.connectedPlayers) + " players")
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerStartGameData:
            dataOk = True
            print("Game start!")
            s.send(GameData.ClientPlayerReadyData(self.playerName).serialize())
            self.status = CLIENT_STATUSES[1]
            self.all_players_ready = True
            self.game_data_copy['player'] = data.players[0]
        if type(data) is GameData.ServerGameStateData:
            dataOk = True
            print("Current player: " + data.currentPlayer)
            print("Player hands: ")
            for p in data.players:
                print(p.toClientString())
            print("Cards in your hand: " + str(data.handSize))
            print("Table cards: ")
            for pos in data.tableCards:
                print(pos + ": [ ")
                for c in data.tableCards[pos]:
                    print(c.toClientString() + " ")
                print("]")
            print("Discard pile: ")
            for c in data.discardPile:
                print("\t" + c.toClientString())
            print("Note tokens used: " + str(data.usedNoteTokens) + "/8")
            print("Storm tokens used: " + str(data.usedStormTokens) + "/3")
        if type(data) is GameData.ServerActionInvalid:
            dataOk = True
            print("Invalid action performed. Reason:")
            print(data.message)
        if type(data) is GameData.ServerActionValid:
            dataOk = True
            print("Action valid!")
            print("Current player: " + data.player)
        if type(data) is GameData.ServerPlayerMoveOk:
            dataOk = True
            print("Nice move!")
            print("Current player: " + data.player)
        if type(data) is GameData.ServerPlayerThunderStrike:
            dataOk = True
            print("OH NO! The Gods are unhappy with you!")
        if type(data) is GameData.ServerHintData:
            dataOk = True
            print("Hint type: " + data.type)
            print("Player " + data.destination + " cards with value " + str(data.value) + " are:")
            for i in data.positions:
                print("\t" + str(i))
        if type(data) is GameData.ServerInvalidDataReceived:
            dataOk = True
            print(data.data)
        if type(data) is GameData.ServerGameOver:
            dataOk = True
            print(data.message)
            print(data.score)
            print(data.scoreMessage)
            stdout.flush()
            self.run = False
            print("Ready for a new game!")
        if not dataOk:
            print("Unknown or unimplemented data type: " + str(type(data)))
        print("[" + self.playerName + " - " + self.status + "]: ", end="")
        stdout.flush()


class ManualClient(Client):
    def __init__(self, playerName, ip, port):
        Client.__init__(self, playerName, ip, port)

    def start(self):
        def manageInput():
            while self.run:
                command = input()
                # Choose data to send
                if command == "exit":
                    self.run = False
                    os._exit(0)
                elif command == "ready" and self.status == CLIENT_STATUSES[0]:
                    s.send(GameData.ClientPlayerStartRequest(self.playerName).serialize())
                elif command == "show" and self.status == CLIENT_STATUSES[1]:
                    s.send(GameData.ClientGetGameStateRequest(self.playerName).serialize())
                elif command.split(" ")[0] == "discard" and self.status == CLIENT_STATUSES[1]:
                    try:
                        cardStr = command.split(" ")
                        cardOrder = int(cardStr[1])
                        s.send(GameData.ClientPlayerDiscardCardRequest(self.playerName, cardOrder).serialize())
                    except:
                        print("Maybe you wanted to type 'discard <num>'?")
                        continue
                elif command.split(" ")[0] == "play" and self.status == CLIENT_STATUSES[1]:
                    try:
                        cardStr = command.split(" ")
                        cardOrder = int(cardStr[1])
                        s.send(GameData.ClientPlayerPlayCardRequest(self.playerName, cardOrder).serialize())
                    except:
                        print("Maybe you wanted to type 'play <num>'?")
                        continue
                elif command.split(" ")[0] == "hint" and self.status == CLIENT_STATUSES[1]:
                    try:
                        destination = command.split(" ")[2]
                        t = command.split(" ")[1].lower()
                        if t != "colour" and t != "color" and t != "value":
                            print("Error: type can be 'color' or 'value'")
                            continue
                        value = command.split(" ")[3].lower()
                        if t == "value":
                            value = int(value)
                            if int(value) > 5 or int(value) < 1:
                                print("Error: card values can range from 1 to 5")
                                continue
                        else:
                            if value not in ["green", "red", "blue", "yellow", "white"]:
                                print("Error: card color can only be green, red, blue, yellow or white")
                                continue
                        s.send(GameData.ClientHintData(self.playerName, destination, t, value).serialize())
                    except:
                        print("Maybe you wanted to type 'hint <type> <destinatary> <value>'?")
                        continue
                elif command == "":
                    print("[" + self.playerName + " - " + self.status + "]: ", end="")
                else:
                    print("Unknown command: " + command)
                    continue
                stdout.flush()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Begin connection
            self.begin_socket_connection(s)

            # Separate thread to get moves from user
            Thread(target=manageInput).start()

            while self.run:
                data = s.recv(DATASIZE)
                if not data:
                    continue
                data = GameData.GameData.deserialize(data)

                self.process_incoming_data(data, s)

if __name__ == '__main__':
    if len(argv) < 4:
        print("You need the player name to start the game.")
        #exit(-1)
        _playerName = "Test" # For debug
        _ip = HOST
        _port = PORT
    else:
        _playerName = argv[3]
        _ip = argv[1]
        _port = int(argv[2])

    client = ManualClient(_playerName, _ip, _port)
    client.start()
