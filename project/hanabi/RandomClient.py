#!/usr/bin/env python3

from random import seed
from random import randint, random

from client import *

seed()

class RandomClient(Client):
    def __init__(self, playerName, ip, port):
        Client.__init__(self, playerName, ip, port)
        self.sent_ready_command = False

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

        def attempt_move():
            command = self.get_random_command()

            if self.sent_ready_command and not (self.game_data_copy['player'] == self.playerName):
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
            # Begin connection
            self.begin_socket_connection(s)

            while self.run:
                # stay idle if I already sent the "ready" command, but other players are not ready
                if self.sent_ready_command & (not self.all_players_ready):
                    continue

                # if everyone is ready, attempt move; return immediately if it's not my turn
                attempt_move()

                data = s.recv(DATASIZE)
                if not data:
                    continue
                data = GameData.GameData.deserialize(data)

                # update own game data copy with any useful info
                for field in vars(data).keys():
                    self.game_data_copy[field] = getattr(data, field, None)

                self.process_incoming_data(data, s)


if __name__ == '__main__':
    _ip = argv[1]
    _port = int(argv[2])
    _n_players = int(argv[3])

    RandomClient(f'client{_n_players}', _ip, _port).start()


