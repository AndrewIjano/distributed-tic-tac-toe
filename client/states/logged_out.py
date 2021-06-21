from client.states.base import State
from client.commands import Command
from client.exceptions import Unauthenticated
from client.states import logged_in


class LoggedOutState(State):
    def handle_input_command(self, command, *args):
        return {
            Command.ADD_USER: self._handle_add_user,
            Command.LOGIN: self._handle_login,
            Command.EXIT: self._handle_exit,
            Command.SKIP: self._handle_skip,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_add_user(self, user, password):
        self.client.server.add_user(user, password)

    def _handle_login(self, user, password):
        try:
            host, port = self.client.address
            self.client.server.login(user, password, host, port)
            self.client.user = user
            self.client.password = password

            self.client.change_state(logged_in.LoggedInState(self.client))
        except Unauthenticated:
            print("Login failed")
