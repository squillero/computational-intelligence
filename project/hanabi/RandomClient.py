#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread
import GameData
import socket
from constants import *
import os

import time
import asyncio


from random import seed
from random import randint, random

from client import *

seed()  # DEBUG

class RandomClient(Client):
    def __init__(self, playerName, ip, port):
        Client.__init__(self, playerName, ip, port)
        self.sent_ready_command = False
        self.all_players_ready = False
        self.game_data_copy = {'player': None, 'usedStormTokens': 0, 'usedNoteTokens': 0}

    def get_random_command(self):
        if not self.sent_ready_command:
            return "ready"

        # TO-DO : add logic to check if move is possible
        move_ok = False
        move = ""
        while not move_ok:
            move = CLIENT_MOVES[randint(1, 2)]
            if (move == 'discard') and (self.game_data_copy['usedNoteTokens'] == 0):
                continue
            if (move == 'hint') and (self.game_data_copy['usedNoteTokens'] == 8):
                continue
            move_ok = True

        if move == "hint":
            return self.build_hint_command()
        elif move == "play":
            return self.build_play_command()
        elif move == "discard":
            return self.build_discard_command()

    def build_hint_command(self, _type, _dest, _payload):
        dest_hand = [] # TO-DO: query it from last game status, given the dest
        if random() > 0.5:
            _type = 'color'
            _payload = CARD_COLORS[randint(0, 4)]
        else:
            _type = 'value'
            _payload = dest_hand[randint(0, 4)]  # hint about a random value from destinatary's existing card numbers
        return f"hint {_type} {_dest} {_payload}"

    def build_discard_command(self, idx=0):
        idx = randint(0, 4)
        return f"discard {idx % 5}"  # force idx bounds-safety

    def build_play_command(self, idx=0):
        idx = randint(0, 4)
        return f"play {idx % 5}"  # force idx bounds-safety

    def start(self):

        def manageInput():
            command = self.get_random_command()

            if self.sent_ready_command and not (self.game_data_copy['player'] == self.playerName):
                #time.sleep(1)
                return

            # Choose data to send
            if command == "exit":
                self.run = False
                os._exit(0)
            elif command == "ready" and self.status == CLIENT_STATUSES[0]:
                self.sent_ready_command = True
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
            elif command.split(" ")[0] == "play" and self.status == CLIENT_STATUSES[1]:
                try:
                    cardStr = command.split(" ")
                    cardOrder = int(cardStr[1])
                    s.send(GameData.ClientPlayerPlayCardRequest(self.playerName, cardOrder).serialize())
                except:
                    print("Maybe you wanted to type 'play <num>'?")
            elif command.split(" ")[0] == "hint" and self.status == CLIENT_STATUSES[1]:
                try:
                    destination = command.split(" ")[2]
                    t = command.split(" ")[1].lower()
                    if t != "colour" and t != "color" and t != "value":
                        print("Error: type can be 'color' or 'value'")
                    value = command.split(" ")[3].lower()
                    if t == "value":
                        value = int(value)
                        if int(value) > 5 or int(value) < 1:
                            print("Error: card values can range from 1 to 5")
                    else:
                        if value not in ["green", "red", "blue", "yellow", "white"]:
                            print("Error: card color can only be green, red, blue, yellow or white")
                    s.send(GameData.ClientHintData(self.playerName, destination, t, value).serialize())
                except:
                    print("Maybe you wanted to type 'hint <type> <destinatary> <value>'?")
            elif command == "":
                print("[" + self.playerName + " - " + self.status + "]: ", end="")
            else:
                print("Unknown command: " + command)
            stdout.flush()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            request = GameData.ClientPlayerAddData(self.playerName)
            s.connect((self.ip, self.port))
            s.send(request.serialize())
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
            if type(data) is GameData.ServerPlayerConnectionOk:
                print("Connection accepted by the server. Welcome " + self.playerName)
            print("[" + self.playerName + " - " + self.status + "]: ", end="")

            while self.run:
                # Stay idle if I already sent the "ready" command, but other players are not ready
                if self.sent_ready_command & (not self.all_players_ready):
                    # time.sleep(2)
                    continue

                manageInput()

                dataOk = False
                data = s.recv(DATASIZE)
                if not data:
                    continue
                data = GameData.GameData.deserialize(data)

                for attr in self.game_data_copy.keys():
                    self.game_data_copy[attr] = getattr(data, attr, self.game_data_copy[attr])

                if type(data) is GameData.ServerPlayerStartRequestAccepted:
                    dataOk = True
                    print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
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

                    #if data.message == "It is not your turn yet":
                    #    time.sleep(2) # TO-DO more elegant!

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
                    print("Unknown or unimplemented data type: " +  str(type(data)))
                print("[" + self.playerName + " - " + self.status + "]: ", end="")
                stdout.flush()

if __name__ == '__main__':
    _ip = argv[1]
    _port = int(argv[2])
    _n_players = int(argv[3])

    RandomClient(f'client_{_n_players}', _ip, _port).start()

    #tasks = []
    #for i in range(0, _n_players):
    #    client = RandomClient(f'client_{i}', _ip, _port)
    #    tasks.append(asyncio.ensure_future( client.start() ))


