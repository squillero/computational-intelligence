#!/usr/bin/env python3

from multiprocessing import Process

from random import seed
from random import randint, random, choice

from client import *

seed(15) # fixed for debug


class RandomClient(Client):
    def __init__(self, playerName, ip, port):
        Client.__init__(self, playerName, ip, port)
        self.sent_ready_command = False
        self.game_data_copy['players'] = []
        self.game_data_copy['player_names'] = []

    @staticmethod
    def get_move_from_hardcoded_p(uniform=False):
        if uniform:
            return choice(CLIENT_MOVES)
        else:
            prob = random()
            if prob > 0.9:
                move = 'play'
            elif prob > 0.3:
                move = 'hint'
            else:
                move = 'discard'
            return move

    @staticmethod
    def build_discard_command():
        idx = randint(0, 4)
        return f"discard {idx % 5}"  # force idx bounds-safety

    @staticmethod
    def build_play_command():
        idx = randint(0, 4)
        return f"play {idx % 5}"  # force idx bounds-safety

    def build_hint_command(self):
        # Pick destinatary at random and query their hand
        # if any information is missing, pull from the server with "show"
        try:
            dest_names = self.get_destinatary_names()
            _dest = choice(dest_names)
            dest_hand = self.get_player_card_colors(_dest)

            if random() > 0.5:
                # hint about a random card color from destinatary's hand
                _type = 'color'
                _payload = choice(dest_hand)
            else:
                # hint about a random card value from destinatary's hand
                _type = 'value'
                _payload = randint(1, 5)

            return f"hint {_type} {_dest} {_payload}"

        except:
            return "show"

    def get_destinatary_names(self):
        return list(filter(lambda n: n != self.playerName, self.game_data_copy['player_names']))

    def get_player_card_colors(self, player_name):
        for player in self.game_data_copy['players']:
            if player.name == player_name:
                return list(map(lambda c: c.color, player.hand))

        return []

    def get_random_command(self):
        if len(self.game_data_copy['players']) == 0:
            return "show"

        move_ok = False
        move = ""
        while not move_ok:
            move = RandomClient.get_move_from_hardcoded_p()
            if (move == 'discard') and (self.game_data_copy['usedNoteTokens'] == 0):
                continue
            if (move == 'hint') and (self.game_data_copy['usedNoteTokens'] == 7):
                continue
            move_ok = True

        if move == "hint":
            return self.build_hint_command()
        elif move == "play":
            return RandomClient.build_play_command()
        elif move == "discard":
            return RandomClient.build_discard_command()

    def start(self):

        def attempt_move(command):
            # return immediately if it's now my turn
            if self.sent_ready_command and not self.is_player_turn():
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

                # Always update own game_data_copy with 'show' before other commands
                # RandomClient's action is at random (with logic checks)
                if not self.sent_ready_command:
                    commands_with_proxy = ["ready", "show"]
                else:
                    commands_with_proxy = ["show", self.get_random_command()]

                for _command in commands_with_proxy:
                    # stay idle if it's not my turn; except if it's a 'show' command
                    if (_command != 'show') & self.sent_ready_command and not self.is_player_turn():
                        continue

                    attempt_move(_command)

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

    if _n_players == 1:
        RandomClient(f'bot-0', _ip, _port).start()
    elif _n_players > 5:
        print("Max players = 5")
        os._exit(0)
    else:
        players = []
        for i in range(0, _n_players):
            p = Process(target=RandomClient(f'random-client-{i}', _ip, _port).start)
            players.append(p)
            players[i].start()

        for i in range(0, len(players)):
            players[i].join()

        print(f"All {_n_players} processes finished")

