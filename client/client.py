from threading import Thread
from random import random

import socket
import sys

from client.dt3p_adapter import Dt3pAdapter
from client.opponent_adapter import OpponentAdapter
from client.commands import Command
from client.exceptions import UserNotActive


class TicTacToePlayer:
    def __init__(self, server_host, server_port) -> None:
        self.server = Dt3pAdapter(server_host, server_port)

        self.listen_sock = self._get_listen_sock()
        self.address = self.listen_sock.getsockname()
        print(self.address)

        self.opponent_sock = None

        self.connection_listening_loop = Thread(target=self.listen_connection, args=())
        self.input_listening_loop = Thread(target=self.listen_input, args=())

        self.state = "unauth"
        self.is_running = True

    def _get_listen_sock(self):
        host = socket.gethostbyname(socket.gethostname())

        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_sock.bind((host, 0))
        listen_sock.settimeout(1)
        listen_sock.listen(5)
        return listen_sock

    def run(self):
        self.connection_listening_loop.start()
        self.input_listening_loop.start()

    def stop(self):
        self.listen_sock.close()

    def listen_connection(self):
        while self.is_running:
            try:
                connection, client_address = self.listen_sock.accept()
                print("accepted")
            except socket.timeout:
                continue

            data = connection.makefile().readline().strip()
            print("received", data)
            if self.state == "auth" and data == "BGIN":
                self.opponent_sock = connection
                print("\rDeseja iniciar uma partida? [y/N] ", end="")
                self.state = "invited"
                self.opponent_listening_loop = Thread(
                    target=self.listen_opponent, args=()
                )
                self.opponent_listening_loop.start()
                continue

            if self.state == "waiting" and data == "":
                pass
            connection.close()

    def listen_opponent(self):
        while data := self.opponent_sock.makefile().readline().strip():
            print("data", data)
            if self.state == "inviting":
                if data == "204 WAIT":
                    print("waiting...")
                    self.state = "waiting"
                if data == "205 PLAY":
                    self.state = "playing"
                if data == "400 NO":
                    print(f"game refused :( {data}")

            if self.state == "waiting":
                command, *args = data.split()
                if command == "SEND":
                    row, col = args
                    print(f"row {row} col {col}")
                    self.state = "playing"

    def listen_input(self):
        while self.is_running:
            input_command = self._get_command()
            try:
                self._handle_command(*input_command)
            except Exception as e:
                print("Invalid arguments", e)

    def _handle_command(self, *input_command):
        return {
            "unauth": self._handle_unauth_command,
            "auth": self._handle_auth_command,
            "invited": self._handle_invited_command,
            "playing": self._handle_playing_command,
            "waiting": self._handle_waiting_command,
            "inviting": self._handle_inviting_command,
        }.get(self.state)(*input_command)

    def _handle_unauth_command(self, command, *args):
        return {
            Command.ADD_USER: self._handle_add_user,
            Command.LOGIN: self._handle_login,
            Command.EXIT: self._handle_exit,
            Command.DEFAULT: self._handle_default,
            Command.SKIP: self._handle_skip,
        }.get(Command(command))(*args)

    def _handle_auth_command(self, command, *args):
        return {
            Command.LIST: self._handle_list,
            Command.BEGIN: self._handle_begin,
            Command.LOGOUT: self._handle_logout,
            Command.EXIT: self._handle_exit,
            Command.DEFAULT: self._handle_default,
            Command.SKIP: self._handle_skip,
        }.get(Command(command))(*args)

    def _handle_playing_command(self, command, *args):
        return {
            Command.SEND: self._handle_send,
            Command.DEFAULT: self._handle_default,
            Command.SKIP: self._handle_skip,
        }.get(Command(command))(*args)

    def _handle_waiting_command(self, command, *args):
        pass

    def _handle_inviting_command(self, command, *args):
        pass

    def _handle_invited_command(self, command):
        if command == "y":
            is_first = random() > 0.5
            if is_first:
                self.opponent_sock.sendall(b"204 WAIT\n")
                self.state = "playing"
            else:
                self.opponent_sock.sendall(b"205 PLAY\n")
                self.state = "waiting"
            return

        self.opponent_sock.sendall(b"400 NO\n")
        self.state = "unauth"

    def _handle_add_user(self, user, password):
        self.server.add_user(user, password)

    def _handle_login(self, user, password):
        host, port = self.address
        self.server.login(user, password, host, port)
        self.user = user
        self.password = password
        self.state = "auth"

    def _handle_logout(self):
        self.server.logout(self.user, self.password)
        self.user = None
        self.password = None
        self.state = "unauth"

    def _handle_list(self):
        active_users = self.server.list_active_users()
        print("status | username")
        print("-----------------")
        for user, status in active_users:
            print(f"  {status}   {user}")
        print("-----------------")

    def _handle_begin(self, opponent_username):
        try:
            opponent_address = self.server.get_user_address(opponent_username)

            self.opponent_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.opponent_sock.connect(opponent_address)
            self.opponent_sock.sendall(b"BGIN\n")

            self.state = "inviting"

            self.opponent_listening_loop = Thread(target=self.listen_opponent, args=())
            self.opponent_listening_loop.start()
        except UserNotActive:
            print("user is not active!")

    def _handle_send(self, row, col):
        self.opponent_sock.sendall(bytes(f"SEND {row} {col}\n", "ascii"))
        self.state = "waiting"

    def _handle_exit(self):
        self.is_running = False

    def _handle_skip(self):
        pass

    def _handle_default(self):
        print("Unknown command!")

    def _get_command(self):
        if self.state in ("waiting", "inviting"):
            return [""]

        return input(f"{self.state}-JogoDaVelha> ").strip().split() or [""]


def run(server_host, server_port):
    player = TicTacToePlayer(server_host, server_port)
    player.run()
