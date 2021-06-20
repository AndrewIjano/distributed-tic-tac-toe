from threading import Thread
from time import time, sleep
from collections import deque
import socket

DELAY_INTERVAL = 1


class OpponentAdapter:
    def __init__(self, connection) -> None:
        self.connection = connection
        self.delays = deque([0, 0, 0])
        self.is_connected = True

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
    
    def end_game(self):
        self._send(b"ENDD\t\n")
        self.close_connection()

    def send_ping(self):
        self._send(b"PING\t\n")
        self.start = time()

    def send_pong(self):
        self._send(b"PONG\t\n")
    
    def receive_pong(self):
        new_measure = (time() - self.start) * 1000
        self.delays.popleft()
        self.delays.append(new_measure)


    def _send(self, message: bytes):
        self.connection.sendall(message)

    def _receive(self) -> str:
        return self.connection.makefile().readline()

    def start_measure_delay(self):
        Thread(target=self.send_pings).start()

    def send_pings(self):
        while self.is_connected:
            self.send_ping()
            sleep(DELAY_INTERVAL)

    def get_command(self):
        conn_input = self._receive().replace("\n", "")
        if conn_input == "":
            return "", [""]
        command, args = conn_input.split("\t")
        return command, args.split()

    def has_accepted_game(self, response):
        return response.split()[0] == "ACPT"

    def close_connection(self):
        self.is_connected = False
        self.connection.close()

    @classmethod
    def from_address(cls, opponent_address):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(opponent_address)
        return cls(connection)
