import unittest
import numpy as np
import GameData
import knowledge


class Card:
	def __init__(self, value, color):
		self.value = value
		self.color = color


class Player:
	def __init__(self, name, hand):
		self.name = name
		self.hand = hand


class State:
	def __init__(self):
		self.discardPile = [Card(2, 'red'), Card(5, 'blue'), Card(4, 'green')]
		self.tableCards = [Card(4, 'blue')]
		p2 = Player('p2', [Card(1, 'red'), Card(4, 'blue'), Card(3, 'white'), Card(2, 'red')])
		p3 = Player('p3', [Card(4, 'white'), Card(1, 'blue'), Card(1, 'green'), Card(5, 'green')])
		p4 = Player('p4', [Card(3, 'red'), Card(4, 'blue'), Card(1, 'green'), Card(3, 'yellow')])
		self.players = [p2, p3, p4]
		self.discardPile = [2]
		self.tableCards = [2]
		self.usedNoteTokens = 1
		self.usedStormTokens = 1


class KnowledgeTest(unittest.TestCase):
	def test_hint(self):
		move_history_hints = [
			GameData.ServerHintData("p0", 'p2', 'color', 'red', [0, 3]),
			GameData.ServerHintData("p0", 'p3', 'value', 1, [1, 2]),
			GameData.ServerHintData("p0", 'p4', 'value', 3, [0, 3]),
			GameData.ServerHintData("p0", 'p1', 'color', 'red', [1]),
			GameData.ServerHintData("p0", 'p1', 'color', 'green', [2]),
			GameData.ServerHintData("p0", 'p1', 'value', 1, [2])
		]
		state = State()

		kmap = knowledge.KnowledgeMap(['p1', 'p2', 'p3', 'p4'], 'p1')
		kmap.updateHands(move_history_hints, state)
		p1 = kmap.getPlayerHand("p1", False)
		p2 = kmap.getPlayerHand("p2", False)
		p3 = kmap.getPlayerHand("p3", False)
		p4 = kmap.getPlayerHand("p4", False)

		p1x = [
			np.array([[0, 0, 0, 0, 0],
					[0, 2, 2, 0, 1],
					[0, 0, 0, 0, 0],
					[0, 2, 1, 2, 1],
					[0, 2, 1, 1, 1]]),
			np.array([[0, 1, 1, 2, 1],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0]]),
			np.array([[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[1, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0]]),
			np.array([[0, 0, 0, 0, 0],
					[0, 2, 2, 0, 1],
					[0, 0, 0, 0, 0],
					[0, 2, 1, 2, 1],
					[0, 2, 1, 1, 1]])
		]

		p2x = [
			np.array([[3, 2, 1, 2, 1],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0]]),
			np.array([[0, 0, 0, 0, 0],
					[2, 2, 2, 1, 1],
					[1, 2, 2, 2, 0],
					[3, 2, 1, 2, 1],
					[3, 2, 2, 1, 1]]),
			np.array([[0, 0, 0, 0, 0],
					[2, 2, 2, 1, 1],
					[1, 2, 2, 2, 0],
					[3, 2, 1, 2, 1],
					[3, 2, 2, 1, 1]]),
			np.array([[3, 2, 1, 2, 1],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0]]),
		]

		p3x = [
			np.array([[0, 1, 1, 2, 1],
					[0, 2, 2, 0, 1],
					[0, 2, 2, 2, 0 + 1],
					[0, 2, 1, 2, 1],
					[0, 2, 1, 2, 1]]),
			np.array([[2, 0, 0, 0, 0],
					[3, 0, 0, 0, 0],
					[2, 0, 0, 0, 0],
					[3, 0, 0, 0, 0],
					[3, 0, 0, 0, 0]]),
			np.array([[2, 0, 0, 0, 0],
					[3, 0, 0, 0, 0],
					[2, 0, 0, 0, 0],
					[3, 0, 0, 0, 0],
					[3, 0, 0, 0, 0]]),
			np.array([[0, 1, 1, 2, 1],
					[0, 2, 2, 0, 1],
					[0, 2, 2, 2, 1],
					[0, 2, 1, 2, 1],
					[0, 2, 1, 2, 1]]),
		]

		p4x = [
			np.array([[0, 0, 2, 0, 0],
					[0, 0, 2, 0, 0],
					[0, 0, 2, 0, 0],
					[0, 0, 2, 0, 0],
					[0, 0, 1, 0, 0]]),
			np.array([[2, 1, 0, 2, 1],
					[2, 2, 0, 1, 1],
					[2, 2, 0, 2, 0],
					[3, 2, 0, 2, 1],
					[3, 2, 0, 1, 1]]),
			np.array([[2, 1, 0, 2, 1],
					[2, 2, 0, 1, 1],
					[2, 2, 0, 2, 0],
					[3, 2, 0, 2, 1],
					[3, 2, 0, 1, 1]]),
			np.array([[0, 0, 2, 0, 0],
					[0, 0, 2, 0, 0],
					[0, 0, 2, 0, 0],
					[0, 0, 2, 0, 0],
					[0, 0, 1, 0, 0]]),
		]

		for i in range(4):
			self.assertTrue((p1[i] == p1x[i]).all())
			self.assertTrue((p2[i] == p2x[i]).all())
			self.assertTrue((p3[i] == p3x[i]).all())
			self.assertTrue((p4[i] == p4x[i]).all())

	def test_play_discard(self):
		state = State()
		move_history_play = [
			GameData.ServerPlayerThunderStrike(player="p0", lastPlayer="p3", card=Card(5, 'blue'), cardHandIndex=1),
			GameData.ServerActionValid(player="p0", lastPlayer="p4", action="a", card=Card(4, 'green'), cardHandIndex=0),
			GameData.ServerActionValid(player="p0", lastPlayer="p2", action="a", card=Card(2, 'red'), cardHandIndex=3)
		]
		kmap = knowledge.KnowledgeMap(['p1', 'p2', 'p3', 'p4'], 'p1')
		kmap.updateHands(move_history_play, state)
		mapx = np.array([[3, 1, 2, 2, 1],
						[3, 2, 2, 2, 0],
						[3, 2, 2, 1, 1],
						[3, 2, 2, 2, 1],
						[3, 2, 2, 2, 1]])
		self.assertTrue((mapx == kmap.matrix).all())


if __name__ == '__main__':
	unittest.main()
