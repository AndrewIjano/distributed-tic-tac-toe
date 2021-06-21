from client.states import logged_in, playing, waiting
from client.board import Board, Mark
from client.states.base import State


class InvitingState(State):
    def get_input_command(self):
        return [""]

    def handle_opponent_command(self, command, *args):
        if command == "ACPT":
            self._handle_invite_accepted(*args)
        elif command == "RFSD":
            self._handle_invite_refused()

    def _handle_invite_accepted(self, action):
        if action == "WAIT":
            self.client.mark = Mark.O
            self.client.change_state(waiting.WaitingState(self.client))
        if action == "PLAY":
            self.client.mark = Mark.X
            self.client.change_state(playing.PlayingState(self.client))
        self.client.board = Board(self.client.mark)
        self.client.opponent.start_measure_delay()

    def _handle_invite_refused(self):
        print(f"Game refused")
        self.client.change_state(logged_in.LoggedInState(self.client))
