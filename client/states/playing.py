from client.states import waiting, logged_in
from client.states.base import State
from client.commands import Command
from client.exceptions import MoveAlreadyDone, MoveOutOfBounds


class PlayingState(State):
    def __init__(self, client) -> None:
        super().__init__(client)
        print(f"Your turn. You are {self.client.mark.value}")

    def handle_input_command(self, command, *args):
        return {
            Command.SEND: self._handle_send,
            Command.DELAY: self._handle_delay,
            Command.END: self._handle_end,
            Command.SKIP: self._handle_skip,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_send(self, row, col):
        try:
            self.client.board.add_move(row, col)
            self.client.opponent.send_move(row, col)
            self.client.board.show()

            if self.client.board.is_game_ended:
                print("It's a tie!" if self.client.board.is_tie else "You win!")
                self.client.opponent.close_connection()
                self.client.server.send_game_result(
                    self.client.user,
                    self.client.opponent.username,
                    is_tie=self.client.board.is_tie,
                )
                self.client.change_state(logged_in.LoggedInState(self.client))
            else:
                self.client.change_state(waiting.WaitingState(self.client))
        except MoveOutOfBounds:
            print(f"Move {row} {col} is out of bounds!")
        except MoveAlreadyDone:
            print(f"Move {row} {col} is already done!")

    def _handle_delay(self):
        print(f"Current measured latency:")
        for delay in self.client.opponent.delays:
            print(f"{delay: 7.3f}ms")

    def _handle_end(self):
        self.client.opponent.end_game()
        self.client.change_state(logged_in.LoggedInState(self.client))
