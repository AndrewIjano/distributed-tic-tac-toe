from server.controllers.users_controller import UsersController

from socketserver import BaseRequestHandler

import logging


class RequestHandler(BaseRequestHandler):
    def __init__(self, *args) -> None:
        self.users_controller = UsersController()
        super().__init__(*args)

    def handle(self) -> None:
        self._handle(self.request)

    def _handle(self, client):
        self.host, _ = client.getsockname()
        logging.info(f"client connected {self.host}")

        command, *args = client.makefile().readline().split()
        command_handler = self._get_command_handler(command)
        response = command_handler(*args)
        client.sendall(response)

    def _get_command_handler(self, command):
        logging.debug(f"received command {command}")
        return {
            "USER": self._handle_add_user,
            "LGIN": self._handle_login,
            "LOUT": self._handle_logout,
            "LIST": self._handle_list_active_users,
            "LEAD": self._handle_list_leaders,
            "ADDR": self._handle_get_user_address,
            "RSLT": self._handle_send_game_result,
        }[command]

    def _handle_add_user(self, username, password) -> bytes:
        self.users_controller.add_user(username, password)
        logging.debug(f"new user {username}")
        return b"201 CREATED"

    def _handle_login(self, username, password, host, port) -> bytes:
        user = self.users_controller.get_user(username)
        if user is not None and user.password == password:
            self.users_controller.set_user_active(username)
            self.users_controller.update_user_address(username, host, port)
            logging.info(f"login succeeded {username} {self.host}")
            return b"200 OK\n"

        logging.info(f"login failed {username} {self.host}")
        return b"401 UNAUTHENTICATED"

    def _handle_logout(self, username, password) -> bytes:
        user = self.users_controller.get_user(username)
        if user.password == password:
            logging.debug(f"new logout {username}")

            self.users_controller.set_user_inactive(username)
            self.users_controller.update_user_address(username, "", "")
            logging.info(f"client disconnected {self.host}")
            return b"200 OK\n"

        return b"401 UNAUTHENTICATED"

    def _handle_list_active_users(self) -> bytes:
        active_users = self.users_controller.get_active_users()

        return bytes(
            "\t".join(f"{u.username} {int(u.is_free)}" for u in active_users),
            "ascii",
        )

    def _handle_list_leaders(self) -> bytes:
        users = self.users_controller.get_users()
        users_sorted_by_points = sorted(users, key=lambda u: u.points, reverse=True)
        return bytes(
            "\t".join(f"{u.username} {u.points}" for u in users_sorted_by_points),
            "ascii",
        )

    def _handle_get_user_address(self, username) -> bytes:
        user = self.users_controller.get_user(username)
        if not user.is_active:
            return b"402 NOT ACTIVE\n"

        return bytes(f"200 OK\t{user.host} {user.port}\n", "ascii")

    def _handle_send_game_result(self, username, opponent, is_tie):
        if not is_tie:
            self.users_controller.increment_user_point(username)

        self.users_controller.set_user_free(username)
        self.users_controller.set_user_free(opponent)

        op_user = self.users_controller.get_user(opponent)
        logging.info(
            f"game ended "
            f"({self.host} {username}) "
            f"({opponent} {op_user.host}) "
            f"winner={None if is_tie else username}"
        )

    def _get_int(self, data_size: int) -> int:
        return int(self._get_str(data_size))

    def _get_str(self, data_size: int) -> str:
        return self.request.recv(data_size).decode("ascii").strip()
