import GameData
from hanabi.GameAdapter import GameAdapter
from hanabi.constants import *
from hanabi.GameAdapter import HintType, Color
from random import choice
import numpy as np
from collections import deque
import sys


class KnowledgeMap:
	"""
		players: use GameAdapter.get_all_players()
		name: name of the playing player
	"""
	def __init__(self, players, name):
		self.name = name
		self.numPlayers = len(players)
		self.numCards = 4 if self.numPlayers > 3 else 5
		self.matrix = np.array([[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1]])
		self.hands = {}
		for player in players:
			self.hands[player] = []
			for _ in range(self.numCards):
				self.hands[player].append(np.ones((5, 5), dtype=bool))

	def __updateHint(self, player, move):
		for i, card in enumerate(self.hands[player]):
			val = move.value - 1 if move.type == 'value' else Color.fromstr(move.value).value
			if i in move.positions:
				if move.type == 'value':
					card[:, :val] = False
					if val < self.numCards - 1:
						card[:, val + 1:] = False
				else:
					card[:val, :] = False
					if val < self.numCards - 1:
						card[val + 1:, :] = False
			else:
				if move.type == 'value':
					card[:, val] = False
				else:
					card[val, :] = False

	def __updateMatrix(self, move):
		self.matrix[Color.fromstr(move.card.color).value, move.card.value-1] -= 1
		self.hands[move.lastPlayer].pop(move.cardHandIndex)
		self.hands[move.lastPlayer].append(np.ones((self.numCards, self.numCards)))

	"""
		Updates the hands of all players looking at the move_history 
		Call this at the start of each iteration (your turn)
	"""
	def updateHands(self, move_history):

		for i in reversed(range(self.numPlayers)):
			if i < len(move_history):
				if type(move_history[-i]) is GameData.ServerHintData:
					self.__updateHint(move_history[-i].destination, move_history[-i])
				elif type(move_history[-i]) in \
						[GameData.ServerPlayerMoveOk, GameData.ServerPlayerThunderStrike, GameData.ServerActionValid]:
					self.__updateMatrix(move_history[-i])
	"""
		target: the player name (string) you want to inspect
		players: state.players
		returns a list of 5x5 matrixes with the probability of each card
	"""
	def getPlayerHand(self, target, players):
		tmpMatrix = self.matrix.copy()
		for player in players:
			if player.name != target:
				for card in player.hand:
					tmpMatrix[Color.fromstr(card.color).value, card.value - 1] -= 1

		# for player in players:
		# 	if player.name == target:
		# 		for card in player.hand:
		# 			self.matrix[Color.fromstr(card.color).value, card.value - 1] += 1
		#
		# if card:
		# 	for player in players:
		# 		if player.name == target:
		# 			mtx: np.ndarray = np.where(self.hands[target][card], self.matrix, 0)
		# 			return mtx / mtx.sum()

		for m in self.hands[target]:
			x = tmpMatrix * m
			y = (tmpMatrix * m).sum()
			z = x/y

		return [tmpMatrix*m / (tmpMatrix*m).sum() for m in self.hands[target]]