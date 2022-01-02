import GameData
from constants import *
from GameAdapter import HintType, Color
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

		name = name of the main player
		players = list of strings with names of ALL players
		numPlayers = number of players in the game
		numCards = number of cards for each player
		hands = dictionary, key = name of a player, value = player's hand
		tableCards = list of cards, containing only the highest value played car for each color
		discardPile = list of discarded cards
		other parameters should not be used
		"""
		self.name = name
		self.players = players
		self.numPlayers = len(players)
		self.numCards = 4 if self.numPlayers > 3 else 5
		self.matrix = np.array([[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1],
								[3, 2, 2, 2, 1]])
		self.numMoves = 0
		self.tableCards = []
		self.discardPile = []
		self.usedNoteTokens = 0
		self.usedStormTokens = 0
		self.hands = {}
		self.hints = {}
		for player in players:
			self.hints[player] = []
			for _ in range(self.numCards):
				self.hints[player].append(np.ones((5, 5), dtype=bool))


	def __updateHint(self, player, move):
		for i, card in enumerate(self.hints[player]):
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
		self.hints[move.lastPlayer].pop(move.cardHandIndex)
		self.hints[move.lastPlayer].append(np.ones((self.numCards, self.numCards), dtype=bool))

	def updateHands(self, move_history, state):
		"""
			Updates the hands of all players looking at the move_history
			Call this at the start of each iteration (your turn)
			@param move_history: move_history from GameAdapter
			@param state: board_state from GameAdapter
		"""


		self.discardPile = state.discardPile
		self.tableCards = state.tableCards
		self.usedNoteTokens = state.usedNoteTokens
		self.usedStormTokens = state.usedStormTokens
		for i in reversed(range(len(move_history) - self.numMoves + 1)):
			if i > 0:
				if type(move_history[-i]) is GameData.ServerHintData:
					self.__updateHint(move_history[-i].destination, move_history[-i])
				elif type(move_history[-i]) in \
						[GameData.ServerPlayerMoveOk, GameData.ServerPlayerThunderStrike, GameData.ServerActionValid]:
					self.__updateMatrix(move_history[-i])
		for player in state.players:
			self.hands[player.name] = player.hand
		self.numMoves = len(move_history)


	def getPlayerHand(self, target, probability=True):
		"""
			Compute probability matrix for each card in the target plater's hand
			@param target: the player name (string) you want to inspect
			@param players: state.players from GameAdapter
			@param probability: if true returns probabilities, otherwise cards
			@return: list(5x5 numpy array)
			In case of less cards in the hand than the maximum number of holdable cards
			the list returned is still as long as the maximum number of cards
			but you should ignore the elements of non-existing cards
		"""
		tmpMatrix = self.matrix.copy()
		for player in self.players:
			if player != target and player != self.name:
				for card in self.hands[player]:
					tmpMatrix[Color.fromstr(card.color).value, card.value - 1] -= 1
		if probability:
			return [tmpMatrix * m / (tmpMatrix * m).sum() for m in self.hints[target]]
		else:
			return [tmpMatrix * m for m in self.hints[target]]

	def getPlayerName(self):
		return self.name

	def getTableCards(self):
		return self.tableCards

	def getDiscardPile(self):
		return self.discardPile

	def getPlayerList(self):
		return self.players

	def getPlayerHands(self):
		return self.hands

	def getStormTokens(self):
		return self.usedStormTokens

	def getNoteTokens(self):
		return self.usedNoteTokens

	def getOnePlayerHand(self, target):
		"""
		@param target: string with name of the player to inspect
		"""
		return self.hands[target]
