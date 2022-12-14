import Quarto
from Player import RandomPlayer

if __name__ == "__main__":
    game = Quarto.Quarto()
    game.set_players((RandomPlayer, RandomPlayer))
    winner = game.run()

    print(f"Winner: player {winner}")
