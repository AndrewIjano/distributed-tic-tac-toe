from enum import Enum
import socket


class OpponentAdapter:
    def __init__(self, connection) -> None:
        self.connection = connection

    def begin_game(self):
        self._send(b"BGIN\n")

    def send_move(self, row, col):
        self._send(bytes(f"SEND\t{row} {col}\n", "ascii"))

    def accept_game_and_wait(self):
        self._send(b"ACPT\tWAIT\n")

    def accept_game_and_play(self):
        self._send(b"ACPT\tPLAY\n")

    def refuse_game(self):
        self._send(b"RFSD\t\n")

    def _send(self, message: bytes):
        self.connection.sendall(message)

    def get_command(self):
        conn_input = self.connection.makefile().readline().replace("\n", "")
        if conn_input == "":
            return "", [""]
        command, args = conn_input.split("\t")
        return command, args.split()

    def has_accepted_game(self, response):
        return response.split()[0] == "ACPT"

    def close_connection(self):
        self.connection.close()

    @classmethod
    def from_address(cls, opponent_address):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(opponent_address)
        return cls(connection)
