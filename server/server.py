from server.heartbeat_service import HeartbeatService
from server.handler import RequestHandler

import socket
import logging

from socketserver import ThreadingTCPServer
from typing import Callable

logger = logging.getLogger(__name__)


class TicTacToeServer(ThreadingTCPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: Callable[..., RequestHandler],
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        HeartbeatService().start()
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(message)s",
            # filename="server.log",
            level=logging.INFO,
        )
        logging.info("application started")


def run(host, port):
    with TicTacToeServer((host, port), RequestHandler) as server:
        server.serve_forever()
