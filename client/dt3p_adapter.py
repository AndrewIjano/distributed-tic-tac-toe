import socket


class Dt3pAdapter:
    def __init__(self, host: str, port: int) -> None:
        self.address = (host, port)

    def add_user(self, user, password):
        self._request(f"USER {len(user):03d} {user} {len(password):03d} {password}")

    def _request(self, message: str):
        print(f"[Dt3pAdapter] sending message: '{message}'")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.sendall(message.encode("ascii"))
            response = s.recv(1024)
        print(f"[Dt3pAdapter] received: {response}")
