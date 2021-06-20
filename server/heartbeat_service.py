from server.controllers.users_controller import UsersController
from server.models.user import User

import socket
import time
import logging
from threading import Thread


INTERVAL = 1


class HeartbeatService(Thread):
    def __init__(self, interval=INTERVAL) -> None:
        super().__init__(target=self._run)

        self.users_controller = UsersController()
        self.interval=interval

    def _run(self):
        while True:
            active_users = self.users_controller.get_active_users()
            for user in active_users:
                self._send_heartbeat(user)
            time.sleep(self.interval)

    def _send_heartbeat(self, user: User):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((user.host, int(user.port)))
                s.sendall(b"HTBT\n")
                response = s.makefile().readline().strip()
                if response != "200 OK":
                    raise Exception()
            except:
                self.users_controller.set_user_inactive(user.username)
                logging.info(f"unexpected client disconnection {user.host}")
