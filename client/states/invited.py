from client.states import logged_in, waiting, playing
from client.board import Board, Mark
from client.states.base import State

from random import random


class InvitedState(State):
    def handle_input_command(self, command):
        if command == "y":
            self._handle_invite_accepted()
        else:
            self._handle_invite_refused()

    def _handle_invite_accepted(self):
        is_player_first = random() > 0.5
        if is_player_first:
            self.client.opponent.accept_game_and_wait()
            self.client.mark = Mark.X
            self.client.change_state(playing.PlayingState(self.client))
        else:
            self.client.opponent.accept_game_and_play()
            self.client.mark = Mark.O
            self.client.change_state(waiting.WaitingState(self.client))
        self.client.opponent.start_measure_delay()
        self.client.board = Board(self.client.mark)

    def _handle_invite_refused(self):
        self.client.opponent.refuse_game()
        self.client.change_state(logged_in.LoggedInState(self.client))
