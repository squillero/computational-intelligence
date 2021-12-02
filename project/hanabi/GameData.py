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
    def __init__(self, sender: str, destination: str, type: str, value, positions: list) -> None:
        action = "Hint data from client to server"
        self.destination = destination
        self.type = type
        self.value = value
        self.positions = positions
        super().__init__(sender, action)

class ClientPlayerAddData(ClientToServerData):
    def __init__(self, sender) -> None:
        action = "Connection request"
        super().__init__(sender, action)

class ClientPlayerStartRequest(ClientToServerData):
    def __init__(self, sender) -> None:
        action = "Player start request"
        super().__init__(sender, action)

class ClientPlayerReadyData(ClientToServerData):
    def __init__(self, sender) -> None:
        action = "Player start status received"
        super().__init__(sender, action)

class ClientPlayerShowCardsRequest(ClientToServerData):
    def __init__(self, sender) -> None:
        action = "Show cards request"
        super().__init__(sender, action)

class ClientPlayerDiscardCardRequest(ClientToServerData):
    def __init__(self, sender, handCardOrdered: int) -> None:
        action = "Discard card request"
        self.handCardOrdered = handCardOrdered
        super().__init__(sender, action)

class ClientPlayerPlayCardRequest(ClientToServerData):
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
    def __init__(self, sender: str, destination: str, type: str, value, positions: list) -> None:
        action = "Hint data from server to destination client"
        self.sender = sender
        self.destination = destination
        self.type = type
        self.value = value
        self.positions = positions
        super().__init__(action)

class ServerPlayerConnectionOk(ServerToClientData):
    def __init__(self, playerName) -> None:
        action = "Connection ok"
        self.message = "Player " + str(playerName) + " connected succesfully!"
        super().__init__(action)

class ServerPlayerStartRequestAccepted(ServerToClientData):
    def __init__(self, connectedPlayers, acceptedStartRequest) -> None:
        action = "Player start request accepted"
        self.connectedPlayers = connectedPlayers
        self.acceptedStartRequests = acceptedStartRequest
        super().__init__(action)

class ServerStartGameData(ServerToClientData):
    def __init__(self, players) -> None:
        action = "Game start"
        self.players = players
        super().__init__(action)

class ServerPlayerHandsData(ServerToClientData):
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
    def __init__(self, player: str) -> None:
        action = "Valid action performed"
        self.player = player
        super().__init__(action)

class ServerPlayerMoveOk(ServerToClientData):
    def __init__(self, player: str) -> None:
        action = "Correct move! Well done!"
        self.player = player
        super().__init__(action)

class ServerPlayerThunderStrike(ServerToClientData):
    def __init__(self) -> None:
        action = "The Gods are angry at you!"
        super().__init__(action)

class ServerActionInvalid(ServerToClientData):
    def __init__(self, msg) -> None:
        action = "Invalid action"
        self.message = msg
        super().__init__(action)

class ServerInvalidDataReceived(ServerToClientData):
    def __init__(self, data) -> None:
        action = "Invalid data received"
        self.data = data
        super().__init__(action)

class ServerGameOver(ServerToClientData):
    def __init__(self, score: int, scoreMessage: str) -> None:
        action = "Game over"
        self.message = "Game over"
        self.score = score
        self.scoreMessage = scoreMessage
        super().__init__(action)