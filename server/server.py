from server.controllers.users_controller import UsersController

from socketserver import BaseRequestHandler, ThreadingTCPServer
from typing import Callable


class RequestHandler(BaseRequestHandler):
    def __init__(self, *args) -> None:
        self.users_controller = UsersController()
        super().__init__(*args)

    def handle(self) -> None:
        command = self._get_str(4)
        command_handler = self._get_command_handler(command)
        response = command_handler()
        self.request.sendall(response)

    def _get_command_handler(self, command):
        print("New command", command)
        return {"USER": self._handle_add_user}[command]

    def _handle_add_user(self) -> bytes:
        user_len = self._get_int(5)
        username = self._get_str(user_len)
        pass_len = self._get_int(5)
        password = self._get_str(pass_len)

        self.users_controller.add_user(username, password)

        print(f"New user '{username}' with password '{password}'")
        return b"201 CREATED"

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
