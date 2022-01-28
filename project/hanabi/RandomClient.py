#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread
import GameData
import socket
from constants import *
import os

from client import Client


class RandomClient(Client):
    def __init__(self, playerName, ip, port):
        Client.__init__(self, playerName, ip, port)
