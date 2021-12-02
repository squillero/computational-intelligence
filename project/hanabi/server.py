import os
import GameData
import socket
from game import Game
import threading
from constants import *
import logging
import sys

# SERVER
playerConnections = {}
game = Game()

playersOk = []

statuses = [
    "Lobby",
    "Game"
]
status = statuses[0]

def manageConnection(conn: socket, addr):
    global status
    with conn:
        logging.info("Connected by: " + str(addr))
        keepActive = True
        playerName = ""
        while keepActive:
            data = conn.recv(DATASIZE)
            if not data:
                del playerConnections[playerName]
                logging.warning("Player disconnected: " + playerName)
                game.removePlayer(playerName)
                keepActive = False
            else:
                data = GameData.GameData.deserialize(data)    
                if status == "Lobby":
                    if type(data) is GameData.ClientPlayerAddData:
                        playerName = data.sender
                        playerConnections[playerName] = (conn, addr)
                        logging.info("Player connected: " + playerName)
                        game.addPlayer(playerName)
                        conn.send(GameData.ServerPlayerConnectionOk(playerName).serialize())
                    elif type(data) is GameData.ClientPlayerStartRequest:
                        game.setPlayerReady(playerName)
                        logging.info("Player ready: " + playerName)
                        conn.send(GameData.ServerPlayerStartRequestAccepted(len(game.getPlayers()), game.getNumReadyPlayers()).serialize())
                        if len(game.getPlayers()) == game.getNumReadyPlayers() and len(game.getPlayers()) > 1:
                            listNames = []
                            for player in game.getPlayers():
                                listNames.append(player.name)
                            logging.info("Game start! Between: " + str(listNames))
                            for player in playerConnections:
                                playerConnections[player][0].send(GameData.ServerStartGameData(listNames).serialize())
                            game.start()
                    # This ensures every player is ready to send requests
                    elif type(data) is GameData.ClientPlayerReadyData:
                        playersOk.append(1)
                    # If every player is ready to send requests, then the game can start
                    if len(playersOk) == len(game.getPlayers()):
                        status = "Game"
                # In game
                elif status == "Game":
                    singleData, multipleData = game.satisfyRequest(data)
                    if singleData is not None:
                        conn.send(singleData.serialize())
                    if multipleData is not None:
                        for id in playerConnections:
                            playerConnections[id][0].send(multipleData.serialize())


def manageInput():
    while True:
        data = input()
        if data == "exit":
            logging.info("Closing the server...")
            os._exit(0)

print("Type 'exit' to end the program")


def manageNetwork():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        logging.info("Hanabi server started on " + HOST + ":" + str(PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            threading.Thread(target=manageConnection, args=(conn, addr)).start()

logging.basicConfig(filename="game.log", level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
threading.Thread(target=manageNetwork).start()
manageInput()