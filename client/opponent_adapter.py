import socket


class OpponentAdapter:
    def __init__(self, host: str, port: int) -> None:
        self.address = (host, port)

    def begin_game(self):
        return self._request("BGIN")

    def send_move(self, row, col):
        return self._request(f"SEND {row} {col}")

    def get_delay(self):
        return self._request("DLAY")

    def end_game(self):
        return self._request("ENDD")

    def _request(self, message: str):
        print(f"[Dt3pAdapter] sending message: '{message}'")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.sendall(message.encode("ascii"))
            response = s.makefile().readline()
        print(f"[Dt3pAdapter] received: {response}")
        return response.strip()
