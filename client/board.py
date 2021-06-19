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
        self.board[row][col] = self.player_mark
        self.turns_count += 1

    def add_opponent_move(self, row, col):
        print(f"[Board] add opponent move row {row} col {col}")
        self.board[row][col] = self.opponent_mark
        self.turns_count += 1

    def show(self):
        print(
            f"\n{'-' * 9}\n".join(
                " | ".join(cell.value for cell in row) for row in self.board
            ),
            end="\n"
        )

    def is_winner(self):
        winner = False
        for i in range(3):
            winner = winner or self.check_row(i)
            winner = winner or self.check_col(i)
        winner = winner or self.check_main_diagonal()
        winner = winner or self.check_anti_diagonal()
        return winner

    def is_tied(self):
        return self.turns_count == 9 and not self.is_winner()

    def check_main_diagonal(self):
        return (
            self.board[0][0] == self.board[1][1] == self.board[2][2] == self.player_mark
        )

    def check_anti_diagonal(self):
        return (
            self.board[2][0] == self.board[1][1] == self.board[0][2] == self.player_mark
        )

    def check_row(self, row):
        return (
            self.board[0][row]
            == self.board[1][row]
            == self.board[2][row]
            == self.player_mark
        )

    def check_col(self, col):
        return (
            self.board[col][0]
            == self.board[col][1]
            == self.board[col][2]
            == self.player_mark
        )
