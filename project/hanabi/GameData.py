# Data to be passed from client to server
import pickle

from constants import DATASIZE

# Generic object
class GameData(object):
    def __init__(self, sender) -> None:
        super().__init__()
        self.sender = sender

    def serialize(self) -> bytes:
        data = pickle.dumps(self)
        datalen = len(data)
        binaryDataLen: bytes  = datalen.to_bytes(2, 'little')
        totdata = bytearray(binaryDataLen) + data
        #ensure no multiple data on same request
        for _ in range(datalen + len(binaryDataLen), DATASIZE):
            totdata.append(0)
        data = bytes(totdata)
        assert(len(data) == DATASIZE)
        return data

    def deserialize(serialized: bytes):
        binarySize = serialized[0:2]
        assert(len(binarySize) == 2)
        datasize = int.from_bytes(binarySize, 'little')
        data = serialized[2:datasize + 2]
        return pickle.loads(data)


# Client to server
class ClientToServerData(GameData):
    def __init__(self, sender, action) -> None:
        super().__init__(sender)
        self.action = action # debug purposes

class ClientHintData(ClientToServerData):
    '''
    The hint data that the client passes to the server. It needs:
    sender: string, name of the sender
    destination: string, name of the destination player
    type: can be "color" or "value"
    value: can be the color or the value of the card
    positions: a list of cards that satisfy the value of the hint (notice, this will probably not be needed anymore)
    '''
    def __init__(self, sender: str, destination: str, type: str, value) -> None:
        action = "Hint data from client to server"
        self.destination = destination
        self.type = type
        self.value = value
        super().__init__(sender, action)

class ClientPlayerAddData(ClientToServerData):
    '''
    A connection request from client to server.
    The client requests the server to be added to the lobby.
    '''
    def __init__(self, sender) -> None:
        action = "Connection request"
        super().__init__(sender, action)

class ClientPlayerStartRequest(ClientToServerData):
    '''
    The client says it's ready to play.
    '''
    def __init__(self, sender) -> None:
        action = "Player start request"
        super().__init__(sender, action)

class ClientPlayerReadyData(ClientToServerData):
    '''
    The response to the server: the player is ready.
    The server needs to know that all players have received 
    the confirmation message to exit the lobby and enter the game.
    '''
    def __init__(self, sender) -> None:
        action = "Player start status received"
        super().__init__(sender, action)

class ClientGetGameStateRequest(ClientToServerData):
    '''
    Used to retrieve the game state.
    '''
    def __init__(self, sender) -> None:
        action = "Show cards request"
        super().__init__(sender, action)

class ClientPlayerDiscardCardRequest(ClientToServerData):
    '''
    Used to discard a card.
    handCardOrdered: the card in hand you want to discard 
            (card 0 is the leftmost, card N is the rightmost).
    '''
    def __init__(self, sender, handCardOrdered: int) -> None:
        action = "Discard card request"
        self.handCardOrdered = handCardOrdered
        super().__init__(sender, action)

class ClientPlayerPlayCardRequest(ClientToServerData):
    '''
    Used to play a card.
    handCardOrdered: the card in hand you want to play 
        (card 0 is the leftmost, card N is the rightmost).
    '''
    def __init__(self, sender, handCardOrdered: int) -> None:
        action = "Play card request"
        self.handCardOrdered = handCardOrdered
        super().__init__(sender, action)

# Server to client
class ServerToClientData(GameData):
    def __init__(self, action) -> None:
        super().__init__("Game Server")
        self.action = action # debug purposes


class ServerHintData(ServerToClientData):
    '''
    The hint data that the server passes to the destination client. It needs:
    sender: string, name of the sender
    destination: string, name of the destination player
    type: can be "color" or "value"
    value: can be the color or the value of the card
    positions: a list of cards that satisfy the value of the hint
    '''

    # ! ADDED 'player: str' so you know the current player (to be consistent with play and discard methods!)
    def __init__(self, sender: str, destination: str, type: str, value, positions: list, player: str) -> None:
        action = "Hint data from server to destination client"
        # ! BUGFIX super.sender overwrites self.sender with 'Game Server', use a different name like 'self.source'
        self.source = sender
        self.destination = destination
        self.type = type
        self.value = value
        self.positions = positions
        # ! ADDED so you know the current player (to be consistent with play and discard methods)
        self.player = player
        super().__init__(action)


class ServerPlayerConnectionOk(ServerToClientData):
    '''
    Server successfully received the connection request from the player.
    You need to tell the server that you are ready.
    '''
    def __init__(self, playerName) -> None:
        action = "Connection ok"
        self.message = "Player " + str(playerName) + " connected succesfully!"
        super().__init__(action)

class ServerPlayerStartRequestAccepted(ServerToClientData):
    '''
    The server acknowledges you are ready.
    connectedPlayers: the number of connected players.
    acceptedStartRequeste: the number of accepted start requests.
    '''
    def __init__(self, connectedPlayers, acceptedStartRequest) -> None:
        action = "Player start request accepted"
        self.connectedPlayers = connectedPlayers
        self.acceptedStartRequests = acceptedStartRequest
        super().__init__(action)

class ServerStartGameData(ServerToClientData):
    '''
    You are not in the lobby anymore. 
    Remember to tell the server that you received this message.
    players: the list of players in turn order.
    '''
    def __init__(self, players) -> None:
        action = "Game start"
        self.players = players
        super().__init__(action)

class ServerGameStateData(ServerToClientData):
    '''
    Shows the game state to the players.
    currentPlayer: the name of the player that should play right now.
    players: the list of players in turn order.
    usedNoteTokens: used blue (note) tokens. 0 is the minimum, 8 is the maximum.
    usedStormTokens: used red (storm) tokens. 0 is the minimum, 3 is the maximum. At 3 the game is over.
    tableCards: shows the cards that are currently being played (forming the current firework).
    discardPile: shows the discard pile.
    NOTE: params might get added on request, if the game allows for it.
    '''
    def __init__(self, currentPlayer: str, players: list, usedNoteTokens: int, usedStormTokens: int, table: list, discard: list) -> None:
        action = "Show cards response"
        self.currentPlayer = currentPlayer
        self.players = players
        self.usedNoteTokens = usedNoteTokens
        self.usedStormTokens = usedStormTokens
        self.tableCards = table
        self.discardPile = discard
        super().__init__(action)


class ServerActionValid(ServerToClientData):
    '''
    Action well performed.
    player: the current player.
    lastPlayer: the player that made the last move.
    action: the actino occurred. Now it is only "discard".
    move: the last move that occurred.
    cardHandIndex: the card index of the lastPlayer played card, given his hand order.
    '''
    # ! ADDED send also length of hand of lastPlayer so to know if drawing occured
    def __init__(self, player: str, lastPlayer: str, action: str, card, cardHandIndex: int, handLength=0) -> None:
        # action = "Valid action performed" #! BUGFIX You are overwriting the action e.g. "discard", so we lose what happened
        self.action = action
        self.card = card
        self.lastPlayer = lastPlayer
        self.cardHandIndex = cardHandIndex
        self.player = player
        # ! ADDED send also length of hand of lastPlayer so to know if drawing occured i.e. you know if there are cards left in the deck
        self.handLength = handLength
        super().__init__(action)


class ServerPlayerMoveOk(ServerToClientData):
    '''
    Play move well performed and successful in game terms. It means a card has been placed successfully.
    player: the current player.
    lastPlayer: the player that made the last move.
    card: the last card played.
    cardHandIndex: the card index of the lastPlayer played card, given his hand order.
    '''
    # ! ADDED send also length of hand of lastPlayer so to know if drawing occured
    def __init__(self, player: str, lastPlayer: str, card, cardHandIndex: int, handLength: int) -> None:
        action = "Correct move! Well done!"
        self.card = card
        self.cardHandIndex = cardHandIndex
        self.lastPlayer = lastPlayer
        self.player = player
        # ! ADDED send also length of hand of lastPlayer so to know if drawing occured
        self.handLength = handLength
        super().__init__(action)


class ServerPlayerThunderStrike(ServerToClientData):
    '''
    Play move well performed, unsuccessful in game terms.
    Adds a red note on the server.
    player: the current player.
    lastPlayer: the player that made the last move.
    card: the card that was just discarded.
    cardHandIndex: the card index of the lastPlayer played card, given his hand order.
    '''
    # ! ADDED send also length of hand of lastPlayer so to know if drawing occured
    def __init__(self, player: str, lastPlayer: str, card, cardHandIndex: int, handLength: int) -> None:
        action = "The Gods are angry at you!"
        self.player = player
        self.lastPlayer = lastPlayer
        self.cardHandIndex = cardHandIndex
        self.card = card
        # ! ADDED send also length of hand of lastPlayer so to know if drawing occured
        self.handLength = handLength
        super().__init__(action)

class ServerActionInvalid(ServerToClientData):
    '''
    Action not performed because it is invalid. Turn is not changed.
    message: error message.
    '''
    def __init__(self, msg) -> None:
        action = "Invalid action"
        self.message = msg
        super().__init__(action)

class ServerInvalidDataReceived(ServerToClientData):
    '''
    Action not performed because of invalid data. turn is not changed.
    data: the invalid data received.
    '''
    def __init__(self, data) -> None:
        action = "Invalid data received"
        self.data = data
        super().__init__(action)

class ServerGameOver(ServerToClientData):
    '''
    The game is over.
    message: "Game over".
    score: the score you reached.
    scoreMessage: the message attached to the score.
    '''
    def __init__(self, score: int, scoreMessage: str) -> None:
        action = "Game over"
        self.message = "Game over"
        self.score = score
        self.scoreMessage = scoreMessage
        super().__init__(action)