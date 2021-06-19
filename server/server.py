from server.controllers.users_controller import UsersController

import socket

from random import random
from socketserver import BaseRequestHandler, ThreadingTCPServer
from typing import Callable


class RequestHandler(BaseRequestHandler):
    def __init__(self, *args) -> None:
        self.users_controller = UsersController()
        super().__init__(*args)

    def handle(self) -> None:
        command, *args = self.request.makefile().readline().split()
        command_handler = self._get_command_handler(command)
        response = command_handler(*args)
        self.request.sendall(response)

    def _get_command_handler(self, command):
        print("New command", command)
        return {
            "USER": self._handle_add_user,
            "LGIN": self._handle_login,
            "LOUT": self._handle_logout,
            "LIST": self._handle_list_active_users,
            "ADDR": self._handle_get_user_address,
        }[command]

    def _handle_add_user(self, username, password) -> bytes:
        self.users_controller.add_user(username, password)

        print(f"New user '{username}' with password '{password}'")
        return b"201 CREATED"

    def _handle_login(self, username, password, host, port) -> bytes:
        user = self.users_controller.get_user(username)
        if user.password == password:
            print(f"New login '{username}' with password '{password}'")
            self.users_controller.set_user_active(username)
            self.users_controller.update_user_address(username, host, port)
            return b"200 OK\n"

        return b"401 UNAUTHENTICATED"

    def _handle_logout(self, username, password) -> bytes:
        user = self.users_controller.get_user(username)
        if user.password == password:
            print(f"New logout '{username}' with password '{password}'")
            self.users_controller.set_user_active(username)
            self.users_controller.update_user_address(username, "", "")
            return b"200 OK\n"

        return b"401 UNAUTHENTICATED"

    def _handle_list_active_users(self) -> bytes:
        active_users = self.users_controller.get_active_users()

        return bytes(
            "".join(f"{u.username} {int(u.is_free)}\t" for u in active_users),
            "ascii",
        )

    def _handle_get_user_address(self, username) -> bytes:
        user = self.users_controller.get_user(username)
        if not user.is_active:
            return b"402 NOT ACTIVE\n"

        return bytes(f"200 OK\t{user.host} {user.port}\n", "ascii")

    def _get_int(self, data_size: int) -> int:
        return int(self._get_str(data_size))

    def _get_str(self, data_size: int) -> str:
        return self.request.recv(data_size).decode("ascii").strip()


class TicTacToeServer(ThreadingTCPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: Callable[..., RequestHandler],
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        print("Server started")


def run(host, port):
    with TicTacToeServer((host, port), RequestHandler) as server:
        server.serve_forever()
