from server.heartbeat_service import HeartbeatService
from server.handler import RequestHandler
from server.secure_handler import SecureRequestHandler

import logging

from socketserver import ThreadingTCPServer
from typing import Callable
from threading import Thread

logger = logging.getLogger(__name__)

HOST = "localhost"

class Worker(ThreadingTCPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: Callable[..., RequestHandler],
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)


class TicTacToeServer:
    def __init__(
        self,
        server_address: tuple[str, int],
        server_secure_address: tuple[str, int],
    ) -> None:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(message)s",
            # filename="server.log",
            level=logging.INFO,
        )
        logging.info("application started")

        worker = Worker(server_address, RequestHandler)
        secure_worker = Worker(server_secure_address, SecureRequestHandler)

        self.threads = (
            Thread(target=worker.serve_forever),
            Thread(target=secure_worker.serve_forever),
            HeartbeatService(),
        )

    def run(self):
        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()


def run(port, port_tls):
    TicTacToeServer(
        server_address=(HOST, port), server_secure_address=(HOST, port_tls)
    ).run()
