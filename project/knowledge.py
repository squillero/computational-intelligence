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
	Contains information about other players hands
	WARNING: this class does not know if the players have less cards in the hand
	than the maximum number of holdable cards(this happens only in end game)
	More information on getPlayerHand description
	"""

	def __init__(self, players, name):
		"""
		@param players: list of all players, obtained with GameAdapter.get_all_players()
		@param name: str, name of the playing player
		"""
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
		self.matrix[Color.fromstr(move.card.color).value, move.card.value - 1] -= 1
		self.hands[move.lastPlayer].pop(move.cardHandIndex)
		self.hands[move.lastPlayer].append(np.ones((self.numCards, self.numCards)))

	def updateHands(self, move_history):
		"""
			Updates the hands of all players looking at the move_history
			Call this at the start of each iteration (your turn)
			@param move_history: move_history from GameAdapter
		"""
		for i in reversed(range(self.numPlayers)):
			if i < len(move_history):
				if type(move_history[-i]) is GameData.ServerHintData:
					self.__updateHint(move_history[-i].destination, move_history[-i])
				elif type(move_history[-i]) in \
						[GameData.ServerPlayerMoveOk, GameData.ServerPlayerThunderStrike, GameData.ServerActionValid]:
					self.__updateMatrix(move_history[-i])

	def getPlayerHand(self, target, players):
		"""
			Compute probability matrix for each card in the target plater's hand
			@param target: the player name (string) you want to inspect
			@param players: state.players
			@return: list(5x5 numpy array)
			In case of less cards in the hand than the maximum number of holdable cards
			the list returned is still as long as the maximum number of cards
			but you should ignore the elements of non-existing cards
		"""
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



		return [tmpMatrix * m / (tmpMatrix * m).sum() for m in self.hands[target]]
