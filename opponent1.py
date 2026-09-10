import numpy as np

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class GomokuAgent:

    def __init__(self, agent_symbol, blank_symbol, opponent_symbol):
        self.name = __name__
        self.agent_symbol = agent_symbol
        self.blank_symbol = blank_symbol
        self.opponent_symbol = opponent_symbol

    def play(self, board):
        board = np.array(board, copy=True)

        for row, col in self._empty_cells(board):
            if self._would_win(board, row, col, self.agent_symbol):
                return (row, col)

        for row, col in self._empty_cells(board):
            if self._would_win(board, row, col, self.opponent_symbol):
                return (row, col)

        return self._best_move(board)

    def _empty_cells(self, board):
        size = len(board)
        return [(r, c) for r in range(size) for c in range(size) if board[r][c] == self.blank_symbol]

    def _line_length(self, board, row, col, symbol):
        size = len(board)
        longest = 1
        for dr, dc in DIRECTIONS:
            length = 1
            for sign in (1, -1):
                r, c = row + dr * sign, col + dc * sign
                while 0 <= r < size and 0 <= c < size and board[r][c] == symbol:
                    length += 1
                    r += dr * sign
                    c += dc * sign
            longest = max(longest, length)
        return longest

    def _would_win(self, board, row, col, symbol):
        board[row][col] = symbol
        try:
            return self._line_length(board, row, col, symbol) >= 5
        finally:
            board[row][col] = self.blank_symbol

    def _nearby_cells(self, board, radius=2):
        size = len(board)
        stones = [(r, c) for r in range(size) for c in range(size) if board[r][c] != self.blank_symbol]
        if not stones:
            return [(size // 2, size // 2)]

        cells = set()
        for r, c in stones:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == self.blank_symbol:
                        cells.add((nr, nc))
        return list(cells)

    def _pattern_value(self, length, open_ends):
        if length >= 5:
            return 1_000_000
        table = {4: (100_000, 10_000), 3: (1_000, 100), 2: (100, 10)}
        if length not in table:
            return 0
        two_open, one_open = table[length]
        return two_open if open_ends == 2 else one_open if open_ends == 1 else 0

    def _score_for(self, board, symbol):
        size = len(board)
        total = 0
        for row in range(size):
            for col in range(size):
                if board[row][col] != symbol:
                    continue
                for dr, dc in DIRECTIONS:
                    pr, pc = row - dr, col - dc
                    if 0 <= pr < size and 0 <= pc < size and board[pr][pc] == symbol:
                        continue  # not the start of this line

                    length, r, c = 0, row, col
                    while 0 <= r < size and 0 <= c < size and board[r][c] == symbol:
                        length += 1
                        r += dr
                        c += dc

                    open_ends = 0
                    if 0 <= r < size and 0 <= c < size and board[r][c] == self.blank_symbol:
                        open_ends += 1
                    if 0 <= pr < size and 0 <= pc < size and board[pr][pc] == self.blank_symbol:
                        open_ends += 1

                    total += self._pattern_value(length, open_ends)
        return total

    def _evaluate(self, board):
        return self._score_for(board, self.agent_symbol) - self._score_for(board, self.opponent_symbol)

    def _minimax(self, board, depth, maximizing):
        size = len(board)
        for row in range(size):
            for col in range(size):
                symbol = board[row][col]
                if symbol != self.blank_symbol and self._line_length(board, row, col, symbol) >= 5:
                    return 1_000_000 if symbol == self.agent_symbol else -1_000_000

        if depth == 0:
            return self._evaluate(board)

        symbol = self.agent_symbol if maximizing else self.opponent_symbol
        results = []
        for row, col in self._nearby_cells(board):
            board[row][col] = symbol
            try:
                results.append(self._minimax(board, depth - 1, not maximizing))
            finally:
                board[row][col] = self.blank_symbol
        return max(results) if maximizing else min(results)

    def _best_move(self, board, depth=2):
        best_score, best_move = float('-inf'), None
        for row, col in self._nearby_cells(board):
            board[row][col] = self.agent_symbol
            try:
                score = self._minimax(board, depth - 1, False)
            finally:
                board[row][col] = self.blank_symbol
            if score > best_score:
                best_score, best_move = score, (row, col)
        return best_move


# ---------------------------------------------------------------
# Run this file directly to play one game: this agent vs dumber_agent.py,
# using the real university engine (gomoku_game.py).
# ---------------------------------------------------------------

if __name__ == "__main__":
    from gomoku_game import GomokuGame, BOARD_SIZE, BLANK_SYMBOL, PLAYER_1_SYMBOL, PLAYER_2_SYMBOL
    from dumber_agent import GomokuAgent as DumberAgent

    p1 = GomokuAgent(PLAYER_1_SYMBOL, BLANK_SYMBOL, PLAYER_2_SYMBOL)
    p2 = DumberAgent(PLAYER_2_SYMBOL, BLANK_SYMBOL, PLAYER_1_SYMBOL)
    game = GomokuGame(p1, p2)

    print("X = opponent.py (this agent)")
    print("O = dumber_agent.py\n")

    turn = 0
    while not game.winner and np.count_nonzero(game.board) != BOARD_SIZE * BOARD_SIZE:
        current = p1 if turn % 2 == 0 else p2
        opponent = p2 if turn % 2 == 0 else p1
        game.board, game.winner, move = game.turn(game.board, current, opponent)
        name = "opponent.py" if current is p1 else "dumber_agent.py"
        print(f"Turn {turn + 1}: {name} played {move}")
        turn += 1

    print()
    symbols = {0: '.', 1: 'X', 2: 'O'}
    for row in game.board:
        print(' '.join(symbols[int(cell)] for cell in row))

    print()
    if game.winner is p1:
        print("Winner: opponent.py")
    elif game.winner is p2:
        print("Winner: dumber_agent.py")
    else:
        print("Draw")
