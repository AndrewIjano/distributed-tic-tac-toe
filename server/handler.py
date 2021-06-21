from server.controllers.users_controller import UsersController
from server.models.response_code import ResponseCode

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
        encoded_response = bytes(f"{response}\n", "ascii")
        client.sendall(encoded_response)

    def _get_command_handler(self, command):
        logging.debug(f"received command {command}")
        return {
            "LIST": self._handle_list_active_users,
            "LEAD": self._handle_list_leaders,
            "ADDR": self._handle_get_user_address,
            "RSLT": self._handle_send_game_result,
        }[command]

    def _handle_list_active_users(self) -> str:
        active_users = self.users_controller.get_active_users()
        encoded_user_list = " ".join(
            f"{u.username}\t{int(u.is_free)}" for u in active_users
        )
        return f"{ResponseCode.OK.value} {encoded_user_list}"

    def _handle_list_leaders(self) -> str:
        users = self.users_controller.get_users()
        users_sorted_by_points = sorted(users, key=lambda u: u.points, reverse=True)
        encoded_leaders_list = " ".join(
            f"{u.username}\t{u.points}" for u in users_sorted_by_points
        )
        return f"{ResponseCode.OK.value} {encoded_leaders_list}"

    def _handle_get_user_address(self, username) -> str:
        user = self.users_controller.get_user(username)
        if not user.is_active:
            return ResponseCode.NOT_ACTIVE.value
        return f"{ResponseCode.OK.value} {user.host} {user.port}"

    def _handle_send_game_result(self, username_1, username_2, is_tie):
        # the first username will never be a loser
        if int(is_tie):
            self.users_controller.increment_user_point(username_1)
            self.users_controller.increment_user_point(username_2)
            winners = (username_1, username_2)
        else:
            self.users_controller.increment_user_point(username_1, point=2)
            winners = username_1

        self.users_controller.set_user_free(username_1)
        self.users_controller.set_user_free(username_2)

        user_2 = self.users_controller.get_user(username_2)
        logging.info(
            f"game ended "
            f"user_1={(self.host, username_1)} "
            f"user_2={(user_2.host, username_2)} "
            f"winner={winners}"
        )
        return ResponseCode.OK.value
