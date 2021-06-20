from client.dt3p_adapter import Dt3pAdapter
from client.opponent_adapter import OpponentAdapter
from client.commands import Command
from client.exceptions import (
    UserNotActive,
    UserIsInvalid,
    MoveAlreadyDone,
    MoveOutOfBounds,
)

from client.board import Board, Mark
from threading import Thread
from random import random
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
            level=logging.INFO,
        )

        self.server = Dt3pAdapter(server_host, server_port, server_port_tls)

        self.listen_sock = self._get_listen_sock()
        self.address = self.listen_sock.getsockname()
        print(self.address)

        self.connection_listening_loop = Thread(target=self.listen_connection, args=())
        self.input_listening_loop = Thread(target=self.listen_input, args=())

        self.state = State.LOGGED_OUT
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
            except socket.timeout:
                continue

            data = connection.makefile().readline().strip()
            command, *args = data.split("\t")

            if command == "HTBT":
                connection.sendall(b"200 OK\n")

            if self.state == State.LOGGED_IN:
                if command == "BGIN":
                    opponent_username, *_ = args
                    print(
                        f"\rDo you you to start a game with '{opponent_username}'? [y/N] ",
                        end="",
                    )
                    self.state = State.INVITED

                    self.opponent = OpponentAdapter(connection, opponent_username)
                    self.opponent_listening_loop = Thread(target=self.listen_opponent)
                    self.opponent_listening_loop.start()
                    continue

            connection.close()

    def listen_opponent(self):
        while self.opponent.is_connected:
            command, args = self.opponent.get_command()

            if command == "PING":
                self.opponent.send_pong()
                continue

            if command == "PONG":
                self.opponent.receive_pong()
                continue

            if self.state == State.INVITING:
                if command == "ACPT":
                    action, *_ = args
                    if action == "WAIT":
                        print("Waiting...")
                        self.mark = Mark.O
                        self.state = State.WAITING
                    if action == "PLAY":
                        self.mark = Mark.X
                        print(f"Your turn. You are {self.mark.value}")
                        self.state = State.PLAYING
                    self.board = Board(self.mark)
                    self.opponent.start_measure_delay()
                elif command == "RFSD":
                    print(f"Game refused")
                    self.state = State.LOGGED_IN

            if self.state == State.WAITING:
                if command == "SEND":
                    self.board.add_opponent_move(*args)
                    self.board.show()
                    if self.board.is_game_ended:
                        print("You lose!")
                        self.opponent.close_connection()
                        self.state = State.LOGGED_IN
                    else:
                        print(f"Your turn. You are {self.mark.value}")
                        self.state = State.PLAYING

                if command == "ENDD":
                    self.opponent.close_connection()
                    self.state = State.LOGGED_IN

    def listen_input(self):
        while self.is_running:
            input_command = self._get_command()
            try:
                self._handle_command(*input_command)
            except TypeError as e:
                print("Invalid arguments:\n", e)
            except Exception as e:
                print("An error occurred:\n", e)

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
            Command.SKIP: self._handle_skip,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_auth_command(self, command, *args):
        return {
            Command.LIST: self._handle_list,
            Command.LEADERS: self._handle_leaders,
            Command.BEGIN: self._handle_begin,
            Command.LOGOUT: self._handle_logout,
            Command.EXIT: self._handle_exit,
            Command.SKIP: self._handle_skip,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_playing_command(self, command, *args):
        return {
            Command.SEND: self._handle_send,
            Command.DELAY: self._handle_delay,
            Command.END: self._handle_end,
            Command.SKIP: self._handle_skip,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_waiting_command(self, command, *args):
        pass

    def _handle_inviting_command(self, command, *args):
        pass

    def _handle_invited_command(self, command):
        if command == "y":
            is_player_first = random() > 0.5
            if is_player_first:
                self.opponent.accept_game_and_wait()
                self.mark = Mark.X
                print(f"Your turn. You are {self.mark.value}")
                self.state = State.PLAYING
            else:
                self.opponent.accept_game_and_play()
                self.mark = Mark.O
                print("Waiting...")
                self.state = State.WAITING
            self.opponent.start_measure_delay()
            self.board = Board(self.mark)
            return

        self.opponent.refuse_game()
        self.state = State.LOGGED_IN

    def _handle_add_user(self, user, password):
        self.server.add_user(user, password)

    def _handle_login(self, user, password):
        host, port = self.address
        success = self.server.login(user, password, host, port)
        if success:
            self.user = user
            self.password = password
            self.state = State.LOGGED_IN
        else:
            print("Login failed")

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
            if opponent_username == self.user:
                raise UserIsInvalid()

            opponent_address = self.server.get_user_address(opponent_username)
            self.opponent = OpponentAdapter.from_address(
                opponent_address, opponent_username
            )
            self.opponent.begin_game(self.user)

            self.state = State.INVITING

            self.opponent_listening_loop = Thread(target=self.listen_opponent)
            self.opponent_listening_loop.start()
        except UserNotActive:
            print("User is not active!")
        except UserIsInvalid:
            print("You can't play with yourself!")

    def _handle_send(self, row, col):
        try:
            self.board.add_move(row, col)
            self.opponent.send_move(row, col)
            self.board.show()

            if self.board.is_game_ended:
                print("It's a tie!" if self.board.is_tie else "You win!")
                self.opponent.close_connection()
                self.server.send_game_result(
                    self.user, self.opponent.username, is_tie=self.board.is_tie
                )
                self.state = State.LOGGED_IN
            else:
                self.state = State.WAITING
        except MoveOutOfBounds:
            print(f"Move {row} {col} is out of bounds!")
        except MoveAlreadyDone:
            print(f"Move {row} {col} is already done!")

    def _handle_delay(self):
        print(f"Current measured latency:")
        for delay in self.opponent.delays:
            print(f"  {delay: 4.3f}ms")

    def _handle_end(self):
        self.opponent.end_game()
        self.state = State.LOGGED_IN

    def _handle_exit(self):
        self.is_running = False

    def _handle_skip(self):
        pass

    def _handle_default(self, *args):
        print("Invalid command!")

    def _get_command(self):
        if self.state in (State.WAITING, State.INVITING):
            return [""]

        return input(f"({self.state.value})-JogoDaVelha> ").strip().split() or [""]


def run(server_host, server_port, server_port_tls):
    player = TicTacToeClient(server_host, server_port, server_port_tls)
    player.run()
