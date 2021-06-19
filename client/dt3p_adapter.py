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

    def get_user_address(self, username):
        response = self._request(f"ADDR {username}\n")
        response_code, *body = response.split("\t")
        if response_code == "200 OK":
            host, port_str = body[0].split()
            return (host, int(port_str))
        raise UserNotActive()

    def begin_game(self):
        return self._request("BGIN\n")

    def send_move(self, row, col):
        return self._request(f"SEND {row} {col}\n")

    def get_delay(self):
        return self._request("DLAY\n")

    def end_game(self):
        return self._request("ENDD\n")

    def _request(self, message: str):
        print(f"[Dt3pAdapter] sending message: '{message}'")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.sendall(message.encode("ascii"))
            response = s.makefile().readline()
        print(f"[Dt3pAdapter] received: {response}")
        return response
