from client.states import playing, logged_in
from client.states.base import State


class WaitingState(State):
    def __init__(self, client) -> None:
        super().__init__(client)
        print("Waiting for your turn...")

    def get_input_command(self):
        return [""]

    def handle_opponent_command(self, command, *args):
        if command == "SEND":
            self._handle_move_sent(*args)
        if command == "ENDD":
            self._handle_game_ended()

    def _handle_move_sent(self, row, col):
        self.client.board.add_opponent_move(row, col)
        self.client.board.show()
        if self.client.board.is_game_ended:
            print("It's a tie!" if self.client.board.is_tie else "You lose!")
            self.client.opponent.close_connection()
            self.client.change_state(logged_in.LoggedInState(self.client))
        else:
            self.client.change_state(playing.PlayingState(self.client))

    def _handle_game_ended(self):
        print(f"Opponent left the game")
        self.client.opponent.close_connection()
        self.client.change_state(logged_in.LoggedInState(self.client))
