from game import *
import GameData

from random import choice, randint

stubs = ['stub1', 'stub2']


class GameWrapper:
    def __init__(self, players=None):
        if players is None:
            players = stubs

        self._game = Game()

        for player in players:
            self._game.addPlayer(player)
            self._game.setPlayerReady(player)

        self.players = self._game.getPlayers()
        self.current_player = self.players[0]

    def getPlayer(self, currentPlayerName: str) -> Player:
        for p in self.players:
            if p.name == currentPlayerName:
                return p

    def getHandColors(self, p):
        return list(set(map(lambda c: c.color, p.hand)))

    def build_play_request(self):
        sender = self.current_player.name
        idx = randint(0, 4)
        return GameData.ClientPlayerPlayCardRequest(sender, idx)

    def build_discard_request(self):
        sender = self.current_player.name
        idx = randint(0, 4)
        return GameData.ClientPlayerDiscardCardRequest(sender, idx)

    def build_hint_request(self):
        sender = self.current_player.name
        filtered_players = list(filter(lambda p: p.name != sender, self.players))
        destination = choice(filtered_players).name

        type = choice(['color', 'value'])
        if type == 'color':
            colors = self.getHandColors(self.getPlayer(destination))
            payload = choice(colors)
        else:
            payload = randint(0, 4)

        return GameData.ClientHintData(sender, destination, type, payload)

    def start(self):
        self._game.start()

        player_idx = 0
        while not self._game.isGameOver():
            self.current_player = self._game.getPlayers()[player_idx % len(self._game.getPlayers())]
            #print(self.current_player)

            moves = ['hint', 'play', 'discard']
            move = choice(moves)

            if move == 'hint':
                r = self.build_hint_request()
            elif move == 'play':
                r = self.build_play_request()
            else:
                r = self.build_discard_request()

            result = self._game.satisfyRequest(r, self.current_player.name)

            print(f"Iteration #{player_idx}, score: {self._game.getScore()}")
            player_idx += 1
            pass

        print(f"Game over - score: {self._game.getScore()}")


w = GameWrapper()
w.start()