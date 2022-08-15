import os
import GameData
import socket
from game import Game
from game import Player
import threading
from constants import *
from signal import signal, SIGPIPE, SIG_DFL
import logging
import sys

mutex = threading.Lock()
# SERVER
playerConnections = {}
game = Game()

mutex = threading.Lock()

playersOk = []

statuses = [
    "Lobby",
    "Game"
]
status = statuses[0]

commandQueue = {}
numPlayers = 2


def manageConnection(conn: socket, addr):
    global status
    global game
    with conn:
        logging.info("Connected by: " + str(addr))
        keepActive = True
        playerName = ""
        while keepActive:
            print("SERVER WAITING")
            data = conn.recv(DATASIZE)

            mutex.acquire(True)

            if not data:
                del playerConnections[playerName]
                logging.warning("Player disconnected: " + playerName)
                game.removePlayer(playerName)
                if len(playerConnections) == 0:
                    logging.info("Shutting down server")
                    os._exit(0)
                keepActive = False
            else:
                print(
                    f"SERVER PROCESSING {GameData.GameData.deserialize(data)}")
                data = GameData.GameData.deserialize(data)
                print(f"SERVER RECEIVED {type(data)} from {data.sender}")
                if status == "Lobby":
                    if type(data) is GameData.ClientPlayerAddData:
                        playerName = data.sender
                        commandQueue[playerName] = []
                        if playerName in playerConnections.keys() or playerName == "" and playerName is None:
                            logging.warning("Duplicate player: " + playerName)
                            conn.send(GameData.ServerActionInvalid(
                                "Player with that name already registered.").serialize())
                            mutex.release()
                            return
                        playerConnections[playerName] = (conn, addr)
                        logging.info("Player connected: " + playerName)
                        game.addPlayer(playerName)
                        conn.send(GameData.ServerPlayerConnectionOk(
                            playerName).serialize())
                    elif type(data) is GameData.ClientPlayerStartRequest:
                        game.setPlayerReady(playerName)
                        logging.info("Player ready: " + playerName)
                        conn.send(GameData.ServerPlayerStartRequestAccepted(
                            len(game.getPlayers()), game.getNumReadyPlayers()).serialize())

                        if len(game.getPlayers()) == game.getNumReadyPlayers() and len(game.getPlayers()) >= numPlayers:
                            listNames = []
                            for player in game.getPlayers():
                                listNames.append(player.name)
                            logging.info(
                                "Game start! Between: " + str(listNames))
                            for player in playerConnections:
                                playerConnections[player][0].send(
                                    GameData.ServerStartGameData(listNames).serialize())
                            game.start()

                    # This ensures every player is ready to send requests
                    elif type(data) is GameData.ClientPlayerReadyData:
                        playersOk.append(1)
                    # If every player is ready to send requests, then the game can start
                    if len(playersOk) == len(game.getPlayers()):
                        status = "Game"
                        for player in commandQueue:
                            for cmd in commandQueue[player]:
                                singleData, multipleData = game.satisfyRequest(
                                    cmd, player)
                                if singleData is not None:
                                    playerConnections[player][0].send(
                                        singleData.serialize())
                                if multipleData is not None:
                                    for id in playerConnections:
                                        playerConnections[id][0].send(
                                            multipleData.serialize())
                                        if game.isGameOver():
                                            os._exit(0)
                        commandQueue.clear()
                    elif type(data) is not GameData.ClientPlayerAddData and type(
                            data) is not GameData.ClientPlayerStartRequest and type(
                            data) is not GameData.ClientPlayerReadyData:
                        commandQueue[playerName].append(data)
                # In game
                elif status == "Game":
                    singleData, multipleData = game.satisfyRequest(
                        data, playerName)
                    if singleData is not None:
                        conn.send(singleData.serialize())
                    if multipleData is not None:
                        for id in playerConnections:
                            playerConnections[id][0].send(
                                multipleData.serialize())
                            if game.isGameOver():
                                logging.info("Game over")
                                logging.info("Game score: " +
                                             str(game.getScore()))
                                # os._exit(0)
                                players = game.getPlayers()
                                game = Game()
                                for player in players:
                                    logging.info("Starting new game")
                                    game.addPlayer(player.name)
                                game.start()
            mutex.release()


def manageInput():
    while True:
        data = input()
        if data == "exit":
            logging.info("Closing the server...")
            os._exit(0)


def manageNetwork():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        logging.info("Hanabi server started on " + HOST + ":" + str(PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            threading.Thread(target=manageConnection,
                             args=(conn, addr)).start()


def start_server(nplayers):
    global numPlayers
    numPlayers = nplayers
    logging.basicConfig(filename="game.log", level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt="%m/%d/%Y %I:%M:%S %p")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    threading.Thread(target=manageNetwork).start()
    manageInput()


if __name__ == '__main__':
    signal(SIGPIPE, SIG_DFL)
    print("Type 'exit' to end the program")
    if len(sys.argv) > 1:
        if int(sys.argv[1]) > 1:
            numPlayers = int(sys.argv[1])

    start_server(numPlayers)
