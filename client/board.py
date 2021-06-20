from client.exceptions import MoveAlreadyDone, MoveOutOfBounds

from enum import Enum


class Mark(Enum):
    X = "x"
    O = "o"
    EMPTY = " "


class GameStatus(Enum):
    WIN = "win"
    LOSE = "lose"
    TIE = "tie"
    PLAYING = "playing"


class Board:
    def __init__(self, player_mark) -> None:
        self.board = [[Mark.EMPTY] * 3 for _ in range(3)]
        self.player_mark = player_mark
        self.opponent_mark = Mark.O if player_mark == Mark.X else Mark.X
        self.turns_count = 0

    def add_move(self, row: str, col: str):
        self._add_move(row, col, self.player_mark)
        print(f"[Board] add move row {row} col {col}")

    def add_opponent_move(self, row: str, col: str):
        self._add_move(row, col, self.opponent_mark)
        print(f"[Board] add opponent move row {row} col {col}")

    def _add_move(self, row: str, col: str, mark):
        row = int(row)
        col = int(col)
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise MoveOutOfBounds()

        if self.board[row][col] != Mark.EMPTY:
            raise MoveAlreadyDone()

        self.board[row][col] = mark
        self.turns_count += 1

    def show(self):
        print(
            "   0   1   2\n"
            + f"\n  {'-' * 11}\n".join(
                f"{idx}  " + f" | ".join(cell.value for cell in row)
                for idx, row in enumerate(self.board)
            )
        )

    @property
    def is_player_winner(self):
        return self._is_winner(mark=self.player_mark)

    @property
    def is_opponent_winner(self):
        return self._is_winner(mark=self.opponent_mark)

    @property
    def is_tie(self):
        return self.game_status == GameStatus.TIE

    @property
    def is_game_ended(self):
        return self.game_status != GameStatus.PLAYING

    @property
    def game_status(self):
        if self.is_player_winner:
            return GameStatus.WIN
        if self.is_opponent_winner:
            return GameStatus.LOSE
        if self.turns_count == 9:
            return GameStatus.TIE
        return GameStatus.PLAYING

    def _is_winner(self, mark):
        winner = False
        for i in range(3):
            winner = winner or self._check_row(i, mark)
            winner = winner or self._check_col(i, mark)
        winner = winner or self._check_main_diagonal(mark)
        winner = winner or self._check_anti_diagonal(mark)
        return winner

    def _check_main_diagonal(self, mark):
        return mark == self.board[0][0] == self.board[1][1] == self.board[2][2]

    def _check_anti_diagonal(self, mark):
        return mark == self.board[2][0] == self.board[1][1] == self.board[0][2]

    def _check_row(self, row, mark):
        return mark == self.board[0][row] == self.board[1][row] == self.board[2][row]

    def _check_col(self, col, mark):
        return mark == self.board[col][0] == self.board[col][1] == self.board[col][2]
