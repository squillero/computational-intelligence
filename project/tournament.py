import os
import subprocess
from datetime import time
from threading import Thread
from time import sleep

import player_Paolo
import player_Dumb

if __name__ == '__main__':
    server = subprocess.Popen('python ./hanabi/server.py')
    t1 = Thread(target=player_Paolo.main)
    #t2 = Thread(target=player_Dumb.main)
    #t1.start()
    t1.start()
    sleep(0.1)
    player_Paolo.main('Stefano')
    t1.join()
    #t2.join()
    server.terminate()


