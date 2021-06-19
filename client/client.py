from threading import Thread
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
        listen_sock.listen()
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

            data = connection.recv(4096).decode("ascii").strip()

            if data == "BGIN":
                self.opponent_sock = connection
                print("\rDeseja iniciar uma partida? [y/N] ", end="")
                self.state = "invited"
                continue
            connection.close()

    def listen_input(self):
        while self.is_running:
            input_command = self._get_command()
            self._handle_command(*input_command)

    def _handle_command(self, *input_command):
        return {
            "unauth": self._handle_unauth_command,
            "auth": self._handle_auth_command,
            "invited": self._handle_invited_command,
            "playing": self._handle_playing_command,
            "waiting": self._handle_waiting_command,
        }.get(self.state)(*input_command)

    def _handle_unauth_command(self, command, *args):
        return {
            Command.ADD_USER: self._handle_add_user,
            Command.LOGIN: self._handle_login,
            Command.EXIT: self._handle_exit,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_auth_command(self, command, *args):
        return {
            Command.LIST: self._handle_list,
            Command.BEGIN: self._handle_begin,
            Command.LOGOUT: self._handle_logout,
            Command.EXIT: self._handle_exit,
        }.get(Command(command), self._handle_default)(*args)

    def _handle_playing_command(self, command, *args):
        pass

    def _handle_waiting_command(self, command, *args):
        pass

    def _handle_invited_command(self, command):
        if command == "y":
            self.opponent_sock.sendall(b"200 OK\n")
            self.state = "playing"
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
            opponent_host, opponent_port = self.server.get_user_address(opponent_username)
            self.opponent = OpponentAdapter(opponent_host, opponent_port)
            response = self.opponent.begin_game()
            if response == "200 OK":
                print("game begin!!")
            else:
                print(f"game refused :( {response}")
        except UserNotActive:
            print("user is not active!")


    def _handle_exit(self):
        self.is_running = False

    def _handle_default(self):
        print("Invalid command!")

    def _get_command(self):
        return input(f"{self.state}-JogoDaVelha> ").strip().split() or [""]


def run(server_host, server_port):
    player = TicTacToePlayer(server_host, server_port)
    player.run()
