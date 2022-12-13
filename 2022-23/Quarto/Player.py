import Quarto
import random
class RandomPlayer(Quarto.Player):

    def __init__(self, quarto: Quarto.Quarto) -> None:
        super.__init__(quarto)
    
    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)
