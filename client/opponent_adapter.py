from threading import Thread
from time import time, sleep
from collections import deque
import socket

DELAY_INTERVAL = 1


class OpponentAdapter:
    def __init__(self, connection, username) -> None:
        self.connection = connection
        self.delays = deque([0, 0, 0])
        self.is_connected = True
        self.username = username
        self.start = time()

    def begin_game(self, player_username):
        self._send(f"BGIN {player_username}")

    def send_move(self, row, col):
        self._send(f"SEND {row} {col}")

    def accept_game_and_wait(self):
        self._send("ACPT WAIT")

    def accept_game_and_play(self):
        self._send("ACPT PLAY")

    def refuse_game(self):
        self._send("RFSD")
    
    def end_game(self):
        self._send("ENDD")
        self.close_connection()
    
    def handle_ping(self, command):
        if command == "PING":
            self.send_pong()
        if command == "PONG":
            self.receive_pong()

    def send_ping(self):
        self._send("PING")
        self.start = time()

    def send_pong(self):
        self._send("PONG")
    
    def receive_pong(self):
        new_measure = (time() - self.start) * 1000
        self.delays.popleft()
        self.delays.append(new_measure)

    def _send(self, message: str):
        if not self.is_connected:
            return
        encoded_message = bytes(f"{message}\n", "ascii")
        self.connection.sendall(encoded_message)

    def _receive(self) -> str:
        if not self.is_connected:
            return "\n"
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
        return conn_input.split()
        # return command, args.split()

    def close_connection(self):
        self.is_connected = False
        self.connection.close()

    @classmethod
    def from_address(cls, opponent_address, opponent_username):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(opponent_address)
        return cls(connection, opponent_username)
