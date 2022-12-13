import Quarto
from Player import RandomPlayer

if __name__ == "__main__":
    game = Quarto.Quarto((RandomPlayer, RandomPlayer))
    winner = game.run()

    print(f"Winner: player {winner}")
