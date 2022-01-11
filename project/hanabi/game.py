from copy import deepcopy
from random import shuffle
import GameData
import logging


class Card(object):
    def __init__(self, id, value, color) -> None:
        super().__init__()
        self.id = id
        self.value = value
        self.color = color

    def toString(self):
        return ("Card " + str(self.id) + "; value: " + str(self.value) + "; color: " + str(self.color))

    def toClientString(self):
        return ("Card " + str(self.value) + " - " + str(self.color))

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id


class Token(object):
    def __init__(self, type) -> None:
        super().__init__()
        self.type = type
        self.flipped = False

    def toString(self):
        return ("Token " + self.type + "; Flipped: " + str(self.flipped))


class Player(object):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        self.ready = False
        self.hand = []

    def takeCard(self, cards):
        self.hand.append(cards.pop())

    def toString(self):
        c = "[ \n\t"
        for card in self.hand:
            c += "\t" + card.toString() + " \n\t"
        c += " ]"
        return ("Player " + self.name + " { \n\tcards: " + c + "\n}")

    def toClientString(self):
        c = "[ \n\t"
        for card in self.hand:
            c += "\t" + card.toClientString() + " \n\t"
        c += " ]"
        return ("Player " + self.name + " { \n\tcards: " + c + "\n}")


class Game(object):

    __dataActions = {}

    __scoreMessages = [
        "Booooooooooooring!",
        "Meh!",
        "Good!",
        "Outstanding!",
        "AMAZING!"
    ]
    __cards = []  # cards are the same for everyone
    __cardsInitialized = False
    __MAX_NOTE_TOKENS = 8
    __MAX_STORM_TOKENS = 3
    __MAX_FIREWORKS = 5

    def __init__(self) -> None:
        super().__init__()
        self.__discardPile = []
        self.__completedFireworks = 0
        # Init cards
        numCards = 0
        if not self.__cardsInitialized:
            self.__cardsInitialized = True
            self.__gameOver = False
            for _ in range(3):
                self.__cards.append(Card(numCards, 1, "red"))
                numCards += 1
                self.__cards.append(Card(numCards, 1, "yellow"))
                numCards += 1
                self.__cards.append(Card(numCards, 1, "green"))
                numCards += 1
                self.__cards.append(Card(numCards, 1, "blue"))
                numCards += 1
                self.__cards.append(Card(numCards, 1, "white"))
                numCards += 1
            for _ in range(2):
                self.__cards.append(Card(numCards, 2, "red"))
                numCards += 1
                self.__cards.append(Card(numCards, 2, "yellow"))
                numCards += 1
                self.__cards.append(Card(numCards, 2, "green"))
                numCards += 1
                self.__cards.append(Card(numCards, 2, "blue"))
                numCards += 1
                self.__cards.append(Card(numCards, 2, "white"))
                numCards += 1
            for _ in range(2):
                self.__cards.append(Card(numCards, 3, "red"))
                numCards += 1
                self.__cards.append(Card(numCards, 3, "yellow"))
                numCards += 1
                self.__cards.append(Card(numCards, 3, "green"))
                numCards += 1
                self.__cards.append(Card(numCards, 3, "blue"))
                numCards += 1
                self.__cards.append(Card(numCards, 3, "white"))
                numCards += 1
            for _ in range(2):
                self.__cards.append(Card(numCards, 4, "red"))
                numCards += 1
                self.__cards.append(Card(numCards, 4, "yellow"))
                numCards += 1
                self.__cards.append(Card(numCards, 4, "green"))
                numCards += 1
                self.__cards.append(Card(numCards, 4, "blue"))
                numCards += 1
                self.__cards.append(Card(numCards, 4, "white"))
                numCards += 1
            for _ in range(1):
                self.__cards.append(Card(numCards, 5, "red"))
                numCards += 1
                self.__cards.append(Card(numCards, 5, "yellow"))
                numCards += 1
                self.__cards.append(Card(numCards, 5, "green"))
                numCards += 1
                self.__cards.append(Card(numCards, 5, "blue"))
                numCards += 1
                self.__cards.append(Card(numCards, 5, "white"))
                numCards += 1
        self.__cardsToDraw = deepcopy(self.__cards)
        self.__tableCards = {
            "red": [],
            "yellow": [],
            "green": [],
            "blue": [],
            "white": []
        }

        ###
        # Init tokens
        self.__noteTokens = 0
        self.__stormTokens = 0
        ###

        # Init players
        self.__players = []
        self.__currentPlayer = 0

        # init game
        self.__started = False

        # score
        self.__score = 0
        # add actions for each class of data
        self.__dataActions[GameData.ClientPlayerDiscardCardRequest] = self.__satisfyDiscardRequest
        self.__dataActions[GameData.ClientGetGameStateRequest] = self.__satisfyShowCardRequest
        self.__dataActions[GameData.ClientPlayerPlayCardRequest] = self.__satisfyPlayCardRequest
        self.__dataActions[GameData.ClientHintData] = self.__satisfyHintRequest

    # Request satisfaction methods
    # Each method produces a tuple of ServerToClientData derivates
    # where the first element is the one to send to a single player, while the second one has to be sent to all players

    def satisfyRequest(self, data: GameData.ClientToServerData, playerName: str):
        if type(data) in self.__dataActions:
            if type(data) == GameData.ClientGetGameStateRequest:
                data.sender = playerName
            return self.__dataActions[type(data)](data)
        else:
            return GameData.ServerInvalidDataReceived(data), None
    # Draw request
    def __satisfyDiscardRequest(self, data: GameData.ClientPlayerDiscardCardRequest):
        player = self.__getCurrentPlayer()
        # It's the right turn to perform an action
        if player.name == data.sender:
            if data.handCardOrdered >= len(player.hand) or data.handCardOrdered < 0:
                return (GameData.ServerActionInvalid("You don't have that many cards!"), None)
            card: Card = player.hand[data.handCardOrdered]
            if not self.__discardCard(card.id, player.name):
                logging.warning(
                    "Impossible discarding a card: there is no used token available")
                return (GameData.ServerActionInvalid("You have no used tokens"), None)
            else:
                self.__drawCard(player.name)
                logging.info("Player: " + self.__getCurrentPlayer().name +
                             ": card " + str(card.id) + " discarded successfully")
                self.__nextTurn()
                # ! ADDED last param. see GameData relative comment in ServerActionValid
                return (None, GameData.ServerActionValid(self.__getCurrentPlayer().name, player.name, "discard", card, data.handCardOrdered, len(player.hand)))
        else:
            return (GameData.ServerActionInvalid("It is not your turn yet"), None)

    # Show request
    def __satisfyShowCardRequest(self, data: GameData.ClientGetGameStateRequest):
        logging.info("Showing hand to: " + data.sender)
        currentPlayer, playerList = self.__getPlayersStatus(data.sender)
        return (GameData.ServerGameStateData(currentPlayer, playerList, self.__noteTokens, self.__stormTokens, self.__tableCards, self.__discardPile), None)

    # Play card request

    def __satisfyPlayCardRequest(self, data: GameData.ClientPlayerPlayCardRequest):
        p = self.__getCurrentPlayer()
        # it's the right turn to perform an action
        if p.name == data.sender:
            if data.handCardOrdered >= len(p.hand) or data.handCardOrdered < 0:
                return (GameData.ServerActionInvalid("You don't have that many cards!"), None)
            card: Card = p.hand[data.handCardOrdered]
            self.__playCard(p.name, data.handCardOrdered)
            ok = self.__checkTableCards()
            self.__gameOver, self.__score = self.__checkGameEnded()
            if self.__gameOver:
                logging.info("Game over, people.")
                logging.info("Please, close the server now")
                logging.info("Score: " + str(self.__score) + "; message: " +
                             self.__scoreMessages[self.__score // len(self.__scoreMessages)])  # ! BUGFIX index
                # ! BUGFIX index
                return (None, GameData.ServerGameOver(self.__score, self.__scoreMessages[self.__score // len(self.__scoreMessages)]))
            if not ok:
                self.__nextTurn()
                # ! ADDED last param. see GameData relative comment of GameData.ServerPlayerThunderStrike
                return (None, GameData.ServerPlayerThunderStrike(self.__getCurrentPlayer().name, p.name, card, data.handCardOrdered, len(p.hand)))
            else:
                logging.info(self.__getCurrentPlayer().name +
                            ": card played and correctly put on the table")
                if card.value == 5:
                    logging.info(card.color + " pile has been filled.")
                    if self.__noteTokens > 0:
                        self.__noteTokens -= 1
                        logging.info("Giving 1 free note token.")
                self.__nextTurn()
                self.__gameOver, self.__score = self.__checkGameEnded()
                # ! ADDED last param. see GameData relative comment of GameData.ServerPlayerMoveOk
                return (None, GameData.ServerPlayerMoveOk(self.__getCurrentPlayer().name, p.name, card, data.handCardOrdered, len(p.hand)))
        else:
            return (GameData.ServerActionInvalid("It is not your turn yet"), None)

    # Satisfy hint request
    def __satisfyHintRequest(self, data: GameData.ClientHintData):
        if self.__getCurrentPlayer().name != data.sender:
            return (GameData.ServerActionInvalid("It is not your turn yet"), None)
        if data.destination == data.sender:
            return (GameData.ServerActionInvalid("You are giving a suggestion to yourself! Bad!"), None)
        if self.__noteTokens == self.__MAX_NOTE_TOKENS:
            logging.warning("All the note tokens have been used. Impossible getting hints")
            return GameData.ServerActionInvalid("All the note tokens have been used"), None
        positions = []
        destPlayer: Player = None
        for p in self.__players:
            if p.name == data.destination:
                destPlayer = p
                break
        if destPlayer is None:
            return GameData.ServerInvalidDataReceived(data="The selected player does not exist"), None

        for i in range(len(destPlayer.hand)):
            if data.type == "color" or data.type == "colour":
                if data.value == destPlayer.hand[i].color:
                    positions.append(i)
            elif data.type == "value":
                if data.value == destPlayer.hand[i].value:
                    positions.append(i)
            else:
                # Backtrack on note token
                self.__noteTokens -= 1
                return GameData.ServerInvalidDataReceived(data=data.type), None
            if data.sender == data.destination:
                self.__noteTokens -= 1
                return GameData.ServerInvalidDataReceived(data="Sender cannot be destination!"), None

        if len(positions) == 0:
            return GameData.ServerInvalidDataReceived(data="You cannot give hints about cards that the other person does not have"), None
        self.__nextTurn()
        self.__noteTokens += 1
        logging.info("Player " + data.sender + " providing hint to " + data.destination + ": cards with " + data.type + " " + str(data.value) + " are in positions: " + str(positions))
        return None, GameData.ServerHintData(data.sender, data.destination, data.type, data.value, positions, self.__getCurrentPlayer().name) #! ADDED last param. see GameData relative comment
 

    def isGameOver(self):
        return self.__gameOver

    # Player functions
    # players list. Not the best, but there are literally max 5 players and the list should give us the order of connection = the order of the rounds
    def addPlayer(self, name: str):
        self.__players.append(Player(name))

    def removePlayer(self, name: str):
        for p in self.__players:
            if p.name == name:
                self.__players.remove(p)
                break
    
    def setPlayerReady(self, name: str):
        for p in self.__players:
            if p.name == name:
                p.ready = True
                break

    def getNumReadyPlayers(self) -> int:
        count = 0
        for p in self.__players:
            if p.ready:
                count += 1
        return count

    def __nextTurn(self):
        self.__currentPlayer += 1
        self.__currentPlayer %= len(self.__players)

    def start(self):
        shuffle(self.__cardsToDraw)
        if len(self.__players) < 2:
            logging.warning("Not enough players!")
            return
        logging.info("Ok, let's start the game!")
        if len(self.__players) < 4:
            for p in self.__players:
                for _ in range(5):
                    p.takeCard(self.__cardsToDraw)
        else:
            for _ in range(4):
                for p in self.__players:
                    p.takeCard(self.__cardsToDraw)
        self.__started = True

    def __getPlayersStatus(self, currentPlayerName):
        players = []
        for p in self.__players:
            #! I WANT ALSO THE ABSOLUTE ORDER OF PLAYERS
            if p.name == currentPlayerName: #! we don't want to cheat
                tmp_player = Player(currentPlayerName) #! so we build an 'empty' Player object for the requesting player
                players.append(tmp_player)
            else:
                players.append(p)
        return (self.__players[self.__currentPlayer].name, players)

    def __getPlayer(self, currentPlayerName: str) -> Player:
        for p in self.__players:
            if p.name == currentPlayerName:
                return p

    def __getCurrentPlayer(self) -> Player:
        return self.__players[self.__currentPlayer]

    def __discardCard(self, cardID: int, playerName: str) -> bool:
        if self.__noteTokens < 1: # Ok only if you already used at least 1 token
            return False
        self.__noteTokens -= 1
        endLoop = False
        # find player
        for p in self.__players:
            if endLoop:
                break
            if p.name == playerName:
                # find card
                for card in p.hand:
                    if endLoop:
                        break
                    if card.id == cardID:
                        self.__discardPile.append(card) # discard
                        p.hand.remove(card) # remove from hand
                        endLoop = True
        return True
    
    def __drawCard(self, playerName: str):
        if len(self.__cardsToDraw) == 0:
            return
        card = self.__cardsToDraw.pop()
        for p in self.__players:
            if p.name == playerName:
                p.hand.append(card)

    def __playCard(self, playerName: str, cardPosition: int):
        p = self.__getPlayer(playerName)
        self.__tableCards[p.hand[cardPosition].color].append(p.hand[cardPosition])
        p.hand.pop(cardPosition)
        if len(self.__cardsToDraw) > 0:
            p.hand.append(self.__cardsToDraw.pop())
    
    def __checkTableCards(self) -> bool:
        for cardPool in self.__tableCards:
            for card in self.__tableCards[cardPool]:
                if len(self.__tableCards[cardPool]) > 0 and self.__tableCards[cardPool][len(self.__tableCards[cardPool]) - 1].value != len(self.__tableCards[cardPool]):
                    self.__tableCards[cardPool].pop()
                    self.__discardPile.append(card)
                    self.__strikeThunder()
                    return False
        return True

    # assumes cards checked
    def __checkFinishedFirework(self, pile) -> bool:
        return len(pile) == 5

    def __strikeThunder(self):
        self.__stormTokens += 1

    def __checkGameEnded(self):
        ended = True
        for pile in self.__tableCards:
            ended = ended and self.__checkFinishedFirework(pile)
        if ended:
            score = 25
            return True, score
        if self.__stormTokens == self.__MAX_STORM_TOKENS:
            return True, 0
        ended = True
        for player in self.__players:
            ended = ended and ((len(player.hand) < 5 and len(self.__players) <= 3) or len(player.hand) < 4)
        if ended:
            score = 0
            for pile in self.__tableCards:
                score += len(self.__tableCards[pile]) #! BUGFIX # instead of 'len(pile)' --> 'pile' is the key (eg. 'red')
            print('Score: ' + str(score))
            return True, score
        return False, 0
    
    def getPlayers(self):
        return self.__players

    def getScore(self):
        return self.__score
