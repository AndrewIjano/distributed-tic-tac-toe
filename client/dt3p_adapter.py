import socket
from client.exceptions import UserNotActive

class Dt3pAdapter:
    def __init__(self, host: str, port: int) -> None:
        self.address = (host, port)

    def add_user(self, username, password):
        response = self._request(
            f"USER {username} {password}\n"
        )

    def login(self, username, password, host, port):
        response = self._request(
            f"LGIN {username} {password} {host} {port}\n"
        )
        return response == "200 OK"
    
    def logout(self, username, password):
        response = self._request(
            f"LOUT {username} {password}\n"
        )

    def list_active_users(self):
        response = self._request(f"LIST\n")
        users_raw = (
            line.split() for line in response.strip().split("\t")
        )
        return [
            (username, "free" if is_free else "busy") for username, is_free in users_raw
        ]
    
    def list_leaders(self):
        response = self._request(f"LEAD\n")
        users_raw = (
            line.split() for line in response.strip().split("\t")
        )
        return [
            (username, int(points)) for username, points in users_raw
        ]

    def get_user_address(self, username):
        response = self._request(f"ADDR {username}\n")
        response_code, *body = response.split("\t")
        if response_code == "200 OK":
            host, port_str = body[0].split()
            return (host, int(port_str))
        raise UserNotActive()

    def send_game_result(self, username, opponent, is_tie):
        self._request(f"RSLT {username} {opponent} {int(is_tie)}")

    def _request(self, message: str):
        encoded_message = message.encode("ascii")
        print(f"[Dt3pAdapter] sending message: '{encoded_message}'")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.sendall(encoded_message)
            response = s.makefile().readline().strip()
        print(f"[Dt3pAdapter] received: {response}")
        return response
