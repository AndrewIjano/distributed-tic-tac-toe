from client.states import invited, inviting, logged_out
from client.states.base import State
from client.commands import Command
from client.opponent_adapter import OpponentAdapter
from client.exceptions import (
    Unauthenticated,
    UserIsInvalid,
    UserNotActive,
    WrongPassword,
)

from threading import Thread


class LoggedInState(State):
    def handle_input_command(self, command, *args):
        return {
            Command.PASSWORD: self._handle_change_password,
            Command.LIST: self._handle_list,
            Command.LEADERS: self._handle_leaders,
            Command.BEGIN: self._handle_begin,
            Command.LOGOUT: self._handle_logout,
            Command.EXIT: self._handle_exit,
            Command.SKIP: self._handle_skip,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_change_password(self, old_password, new_password):
        try:
            self.client.server.change_password(
                self.client.user, old_password, new_password
            )
            self.client.password = new_password
        except WrongPassword:
            print("The current password is wrong")

    def _handle_logout(self):
        try:
            self.client.server.logout(self.client.user, self.client.password)
            self.client.user = None
            self.client.password = None
            self.client.change_state(logged_out.LoggedOutState(self.client))
        except Unauthenticated:
            print("Logout failed")

    def _handle_list(self):
        active_users = self.client.server.list_active_users()
        print("status | username")
        print("-----------------")
        for user, status in active_users:
            print(f"  {status}   {user}")
        print("-----------------")

    def _handle_leaders(self):
        leaders = self.client.server.list_leaders()
        print("username | points")
        print("-----------------")
        for user, points in leaders:
            print(f"{user: <10}\t{points: <10}")
        print("-----------------")

    def _handle_begin(self, opponent_username):
        try:
            if opponent_username == self.client.user:
                raise UserIsInvalid()

            opponent_address = self.client.server.get_user_address(opponent_username)
            self.client.opponent = OpponentAdapter.from_address(
                opponent_address, opponent_username
            )
            self.client.opponent.begin_game(self.client.user)
            self.client.add_thread(Thread(target=self.client.listen_opponent))
            self.client.change_state(inviting.InvitingState(self.client))
        except UserNotActive:
            print("User is not active!")
        except UserIsInvalid:
            print("You can't play with yourself!")

    def handle_new_connection_command(self, connection, command, *args):
        if command == "BGIN":
            self._handle_received_begin(connection, *args)

    def _handle_received_begin(self, connection, opponent_username):
        print(
            f"\rDo you you to start a game with '{opponent_username}'? [y/N] ",
            end="",
        )

        self.client.opponent = OpponentAdapter(connection, opponent_username)
        self.client.add_thread(Thread(target=self.client.listen_opponent))
        self.client.change_state(invited.InvitedState(self.client))
