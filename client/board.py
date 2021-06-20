from enum import Enum


class Mark(Enum):
    X = "x"
    O = "o"
    EMPTY = " "


class Board:
    def __init__(self, player_mark) -> None:
        self.board = [[Mark.EMPTY] * 3 for _ in range(3)]
        self.player_mark = player_mark
        self.opponent_mark = Mark.O if player_mark == Mark.X else Mark.X
        self.turns_count = 0

    def add_move(self, row, col):
        print(f"[Board] add move row {row} col {col}")
        self.board[int(row)][int(col)] = self.player_mark
        self.turns_count += 1

    def add_opponent_move(self, row, col):
        print(f"[Board] add opponent move row {row} col {col}")
        self.board[int(row)][int(col)] = self.opponent_mark
        self.turns_count += 1

    def show(self):
        print(
            "   0   1   2\n"
            + f"\n  {'-' * 11}\n".join(
                f"{idx}  " + f" | ".join(cell.value for cell in row)
                for idx, row in enumerate(self.board)
            )
        )

    def is_player_winner(self):
        return self.is_winner(mark=self.player_mark)

    def is_opponent_winner(self):
        return self.is_winner(mark=self.opponent_mark)

    def is_tied(self):
        return self.turns_count == 9 and not self.is_winner()

    def is_winner(self, mark):
        winner = False
        for i in range(3):
            winner = winner or self.check_row(i, mark)
            winner = winner or self.check_col(i, mark)
        winner = winner or self.check_main_diagonal(mark)
        winner = winner or self.check_anti_diagonal(mark)
        return winner

    def check_main_diagonal(self, mark):
        return mark == self.board[0][0] == self.board[1][1] == self.board[2][2]

    def check_anti_diagonal(self, mark):
        return mark == self.board[2][0] == self.board[1][1] == self.board[0][2]

    def check_row(self, row, mark):
        return mark == self.board[0][row] == self.board[1][row] == self.board[2][row]

    def check_col(self, col, mark):
        return mark == self.board[col][0] == self.board[col][1] == self.board[col][2]
