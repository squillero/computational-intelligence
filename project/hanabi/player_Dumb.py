from project.hanabi.GameAdapter import GameAdapter
from constants import *
from project.hanabi.GameAdapter import HintType
from random import choice
import sys

if __name__ == '__main__':
    name = 'Paolo'
    if len(sys.argv) > 1:
        name = sys.argv[1]
    start_dict = {
        'name': name,
        'ip': HOST,
        'port': PORT,
        'datasize': DATASIZE
    }
    manager = GameAdapter(**start_dict)
    players = manager.get_other_players()
    for state, move_history in manager:
        move = choice(('Hint', 'Play', 'Discard'))
        if move == 'Hint':
            rec = choice(players)
            type_hint = choice([HintType.COLOR, HintType.NUMBER])
            value = choice([0, 1, 2, 3, 4]) if type_hint == HintType.NUMBER else choice(['red', 'blue', 'yellow', 'white', 'green'])
            manager.send_hint(rec, type_hint, value)
        elif move == 'Play':
            value = choice([0, 1, 2, 3, 4])
            manager.play_card(value)
        elif move == 'Discard':
            value = choice([0, 1, 2, 3, 4])
            manager.discard_card(value)