
import numpy as np
from gomoku_game import GomokuGame, BOARD_SIZE, BLANK_SYMBOL, PLAYER_1_SYMBOL, PLAYER_2_SYMBOL
from opponent import GomokuAgent as OurAgent
from dumb import GomokuAgent as DumberAgent


def print_board(board):
    symbols = {0: '.', 1: 'X', 2: 'O'}
    for row in board:
        print(' '.join(symbols[int(cell)] for cell in row))
    print()


def main():
    p1 = OurAgent(PLAYER_1_SYMBOL, BLANK_SYMBOL, PLAYER_2_SYMBOL)
    p2 = DumberAgent(PLAYER_2_SYMBOL, BLANK_SYMBOL, PLAYER_1_SYMBOL)

    game = GomokuGame(p1, p2)
    turn = 0

    print("X = opponent.py (our agent)")
    print("O = dumber_agent.py\n")

    while not game.winner and np.count_nonzero(game.board) != BOARD_SIZE * BOARD_SIZE:
        current = p1 if turn % 2 == 0 else p2
        opponent = p2 if turn % 2 == 0 else p1

        game.board, game.winner, move = game.turn(game.board, current, opponent)
        name = "opponent.py" if current is p1 else "dumber_agent.py"
        print(f"Turn {turn + 1}: {name} played {move}")

        turn += 1

    print()
    print_board(game.board)

    if game.winner is p1:
        print("Winner: opponent.py")
    elif game.winner is p2:
        print("Winner: dumber_agent.py")
    else:
        print("Draw")


if __name__ == "__main__":
    main()