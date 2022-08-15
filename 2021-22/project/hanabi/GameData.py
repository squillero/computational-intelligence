# Data to be passed from client to server
import pickle

# Generic object
class GameData(object):
    def __init__(self, sender) -> None:
        super().__init__()
        self.sender = sender

    def serialize(self) -> str:
        return pickle.dumps(self)

    def deserialize(serialized: str):
        return pickle.loads(serialized)


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
    def __init__(self, sender: str, destination: str, type: str, value, positions: list) -> None:
        action = "Hint data from server to destination client"
        self.sender = sender
        self.destination = destination
        self.type = type
        self.value = value
        self.positions = positions
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
    Action well performed
    '''
    def __init__(self, player: str) -> None:
        action = "Valid action performed"
        self.player = player
        super().__init__(action)

class ServerPlayerMoveOk(ServerToClientData):
    '''
    Play move well performed and successful in game terms.
    player: the current player.
    '''
    def __init__(self, player: str) -> None:
        action = "Correct move! Well done!"
        self.player = player
        super().__init__(action)

class ServerPlayerThunderStrike(ServerToClientData):
    '''
    Play move well performed, unsuccessful in game terms.
    Adds a red note on the server.
    '''
    def __init__(self) -> None:
        action = "The Gods are angry at you!"
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