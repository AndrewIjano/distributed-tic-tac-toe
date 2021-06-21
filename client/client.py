from client.states.logged_out import LoggedOutState
from client.dt3p_adapter import Dt3pAdapter

from threading import Thread
from enum import Enum

import socket
import logging


class State(Enum):
    LOGGED_OUT = "logged out"
    LOGGED_IN = "logged in"
    INVITED = "invited"
    PLAYING = "playing"
    WAITING = "waiting"
    INVITING = "inviting"


class TicTacToeClient:
    def __init__(self, server_host, server_port, server_port_tls) -> None:
        logging.basicConfig(
            format="%(message)s",
            level=logging.DEBUG,
        )

        self.server = Dt3pAdapter(server_host, server_port, server_port_tls)
        self.listen_sock = self._get_listen_sock()
        self.address = self.listen_sock.getsockname()

        self.threads = [
            Thread(target=self.listen_connection),
            Thread(target=self.listen_input),
        ]

        self.state = LoggedOutState(client=self)

    def _get_listen_sock(self):
        host = socket.gethostbyname(socket.gethostname())

        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_sock.bind((host, 0))
        listen_sock.settimeout(1)
        listen_sock.listen(5)
        return listen_sock

    def run(self):
        self.is_running = True
        for thread in self.threads:
            thread.start()

        for t in self.threads:
            t.join()
        self.listen_sock.close()

    def add_thread(self, thread: Thread):
        thread.start()

    def stop(self):
        self.is_running = False

    def listen_connection(self):
        while self.is_running:
            try:
                connection, client_address = self.listen_sock.accept()
            except socket.timeout:
                continue

            data = connection.makefile().readline().strip()
            command, *args = data.split()

            if command == "HTBT":
                connection.sendall(b"200_OK\n")
                connection.close()

            self.state.handle_new_connection_command(connection, command, *args)

    def listen_opponent(self):
        while self.opponent.is_connected:
            command, *args = self.opponent.get_command()
            self.opponent.handle_ping(command)
            self.state.handle_opponent_command(command, *args)

    def listen_input(self):
        while self.is_running:
            input_command = self.state.get_input_command()
            try:
                self.state.handle_input_command(*input_command)
            except TypeError as e:
                print("Invalid arguments:\n", e)
            except Exception as e:
                print("An error occurred:\n", e)

    def change_state(self, state):
        self.state = state


def run(server_host, server_port, server_port_tls):
    player = TicTacToeClient(server_host, server_port, server_port_tls)
    player.run()
