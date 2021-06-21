from server.handler import RequestHandler

from ssl import SSLContext, PROTOCOL_TLS_SERVER

import logging

class SecureRequestHandler(RequestHandler):
    def handle(self) -> None:
        context = SSLContext(PROTOCOL_TLS_SERVER)
        context.load_cert_chain("cert/cert.pem", "cert/key.pem")

        with context.wrap_socket(self.request, server_side=True) as tls:
            self._handle(client=tls)

    def _get_command_handler(self, command):
        logging.debug(f"received command {command}")
        return {
            "USER": self._handle_add_user,
            "PASS": self._handle_change_password,
            "LGIN": self._handle_login,
            "LOUT": self._handle_logout,
        }[command]

    def _handle_add_user(self, username, password) -> bytes:
        self.users_controller.add_user(username, password)
        logging.debug(f"new user {username}")
        return b"201 CREATED"
    
    def _handle_change_password(self, username, old_password, new_password) -> bytes:
        user = self.users_controller.get_user(username)
        if user is not None and user.password == old_password:
            self.users_controller.update_user_password(username, new_password)
            logging.debug(f"password updated {username}")
            return b"200 OK\n"
        return b"401 UNAUTHENTICATED\n"

    def _handle_login(self, username, password, host, port) -> bytes:
        user = self.users_controller.get_user(username)
        if user is not None and user.password == password:
            self.users_controller.set_user_active(username)
            self.users_controller.update_user_address(username, host, port)
            logging.info(f"login succeeded {username} {self.host}")
            return b"200 OK\n"

        logging.info(f"login failed {username} {self.host}")
        return b"401 UNAUTHENTICATED\n"

    def _handle_logout(self, username, password) -> bytes:
        user = self.users_controller.get_user(username)
        if user.password == password:
            logging.debug(f"new logout {username}")

            self.users_controller.set_user_inactive(username)
            self.users_controller.update_user_address(username, "", "")
            logging.info(f"client disconnected {self.host}")
            return b"200 OK\n"

        return b"401 UNAUTHENTICATED\n"