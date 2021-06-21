from client.exceptions import UserNotActive

from ssl import SSLContext, PROTOCOL_TLS_CLIENT, get_server_certificate

import socket
import logging

logger = logging.getLogger("Dt3pAdapter")


class Dt3pAdapter:
    def __init__(self, host: str, port: int, port_tls: int) -> None:
        self.hostname = host
        self.address = (host, port)
        self.secure_address = (host, port_tls)
        self.context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.context.load_verify_locations("cert/cert.pem")

    def add_user(self, username, password):
        response = self._secure_request(f"USER {username} {password}\n")

    def login(self, username, password, host, port):
        response = self._secure_request(f"LGIN {username} {password} {host} {port}\n")
        return response == "200 OK"

    def logout(self, username, password):
        response = self._secure_request(f"LOUT {username} {password}\n")

    def list_active_users(self):
        response = self._request(f"LIST\n")
        users_raw = (line.split() for line in response.strip().split("\t"))
        return [
            (username, "free" if is_free else "busy") for username, is_free in users_raw
        ]

    def list_leaders(self):
        response = self._request(f"LEAD\n")
        users_raw = (line.split() for line in response.strip().split("\t"))
        return [(username, int(points)) for username, points in users_raw]

    def get_user_address(self, username):
        response = self._request(f"ADDR {username}\n")
        response_code, *body = response.split("\t")
        if response_code == "200 OK":
            host, port_str = body[0].split()
            return (host, int(port_str))
        raise UserNotActive()

    def send_game_result(self, username, opponent, is_tie):
        self._request(f"RSLT {username} {opponent} {int(is_tie)}\n")

    def _request(self, message: str):
        with socket.create_connection(self.address) as s:
            return self._make_request(s, message)

    def _secure_request(self, message: str):
        with socket.create_connection(self.secure_address) as sock:
            with self.context.wrap_socket(sock, server_hostname=self.hostname) as tls:
                return self._make_request(tls, message)

    def _make_request(self, sock, message):
        encoded_message = message.encode("ascii")
        logger.debug(f"sending message: '{encoded_message}'")
        sock.sendall(encoded_message)
        response = sock.makefile().readline().strip()
        logger.debug(f"received: {response}")
        return response
