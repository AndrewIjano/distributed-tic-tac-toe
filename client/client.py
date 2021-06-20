from threading import Thread
from random import random

from enum import Enum

import socket
import sys

from client.dt3p_adapter import Dt3pAdapter
from client.opponent_adapter import OpponentAdapter
from client.commands import Command
from client.exceptions import UserNotActive
from client.board import Board, Mark


class State(Enum):
    LOGGED_OUT = "logged out"
    LOGGED_IN = "logged in"
    INVITED = "invited"
    PLAYING = "playing"
    WAITING = "waiting"
    INVITING = "inviting"


class TicTacToeClient:
    def __init__(self, server_host, server_port) -> None:
        self.server = Dt3pAdapter(server_host, server_port)

        self.listen_sock = self._get_listen_sock()
        self.address = self.listen_sock.getsockname()
        print(self.address)

        self.opponent_sock = None

        self.connection_listening_loop = Thread(target=self.listen_connection, args=())
        self.input_listening_loop = Thread(target=self.listen_input, args=())

        self.state = State.LOGGED_OUT
        self.is_running = True
        self.is_playing = False

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
            except socket.timeout:
                continue

            data = connection.makefile().readline().strip()
            if self.state == State.LOGGED_IN:
                if data == "BGIN":
                    print("\rDeseja iniciar uma partida? [y/N] ", end="")
                    self.state = State.INVITED

                    self.opponent = OpponentAdapter(connection)
                    self.opponent_listening_loop = Thread(
                        target=self.listen_opponent, args=()
                    )
                    self.opponent_listening_loop.start()
                    continue
            connection.close()

    def listen_opponent(self):
        self.is_playing = True
        while self.is_playing:
            command, args = self.opponent.get_command()

            if self.state == State.INVITING:
                if command == "ACPT":
                    action, *_ = args
                    if action == "WAIT":
                        print("waiting...")
                        self.mark = Mark.O
                        self.state = State.WAITING
                    if action == "PLAY":
                        self.mark = Mark.X
                        self.state = State.PLAYING
                    self.board = Board(self.mark)
                else:
                    print(f"game refused :( {command}")

            if self.state == State.WAITING:
                if command == "SEND":
                    self.board.add_opponent_move(*args)
                    self.board.show()
                    if self.board.is_opponent_winner():
                        print("You lose!")
                        self.opponent.close_connection()
                        self.is_playing = False
                        self.state = State.LOGGED_IN
                    else:
                        self.state = State.PLAYING

    def listen_input(self):
        while self.is_running:
            input_command = self._get_command()
            try:
                self._handle_command(*input_command)
            except Exception as e:
                print("Invalid arguments", e)

    def _handle_command(self, *input_command):
        return {
            State.LOGGED_OUT: self._handle_unauth_command,
            State.LOGGED_IN: self._handle_auth_command,
            State.INVITED: self._handle_invited_command,
            State.PLAYING: self._handle_playing_command,
            State.WAITING: self._handle_waiting_command,
            State.INVITING: self._handle_inviting_command,
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
            Command.LEADERS: self._handle_leaders,
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
            is_player_first = random() > 0.5
            if is_player_first:
                self.opponent.accept_game_and_wait()
                self.state = State.PLAYING
                self.mark = Mark.X
            else:
                self.opponent.accept_game_and_play()
                self.state = State.WAITING
                self.mark = Mark.O
            self.board = Board(self.mark)
            return

        self.opponent.refuse_game()
        self.state = State.LOGGED_IN

    def _handle_add_user(self, user, password):
        self.server.add_user(user, password)

    def _handle_login(self, user, password):
        host, port = self.address
        self.server.login(user, password, host, port)
        self.user = user
        self.password = password
        self.state = State.LOGGED_IN

    def _handle_logout(self):
        self.server.logout(self.user, self.password)
        self.user = None
        self.password = None
        self.state = State.LOGGED_OUT

    def _handle_list(self):
        active_users = self.server.list_active_users()
        print("status | username")
        print("-----------------")
        for user, status in active_users:
            print(f"  {status}   {user}")
        print("-----------------")
    
    def _handle_leaders(self):
        leaders = self.server.list_leaders()
        print("username | points")
        print("-----------------")
        for user, points in leaders:
            print(f"{user: <10}\t{points: <10}")
        print("-----------------")

    def _handle_begin(self, opponent_username):
        try:
            opponent_address = self.server.get_user_address(opponent_username)
            self.opponent = OpponentAdapter.from_address(opponent_address)
            self.opponent.begin_game()

            self.state = State.INVITING

            self.opponent_listening_loop = Thread(target=self.listen_opponent, args=())
            self.opponent_listening_loop.start()
        except UserNotActive:
            print("user is not active!")

    def _handle_send(self, row, col):
        self.board.add_move(row, col)
        self.opponent.send_move(row, col)
        self.board.show()

        if self.board.is_player_winner():
            print("You win!")
            self.opponent.close_connection()
            self.is_playing = False
            self.server.send_game_result(self.user, "aaa", is_tie=False)
            self.state = State.LOGGED_IN
        elif self.board.is_tied():
            print("It's a tie!")
            self.opponent.close_connection()
            self.is_playing = False
            self.server.send_game_result(self.user, "aaa", is_tie=True)
            self.state = State.LOGGED_IN
        else:
            self.state = State.WAITING

    def _handle_exit(self):
        self.is_running = False

    def _handle_skip(self):
        pass

    def _handle_default(self):
        print("Unknown command!")

    def _get_command(self):
        if self.state in (State.WAITING, State.INVITING):
            return [""]

        return input(f"({self.state.value})-JogoDaVelha> ").strip().split() or [""]


def run(server_host, server_port):
    player = TicTacToeClient(server_host, server_port)
    player.run()
