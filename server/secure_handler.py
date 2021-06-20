from server.handler import RequestHandler

from ssl import SSLContext, PROTOCOL_TLS_SERVER


class SecureRequestHandler(RequestHandler):
    def handle(self) -> None:
        context = SSLContext(PROTOCOL_TLS_SERVER)
        context.load_cert_chain("cert.pem", "key.pem")

        with context.wrap_socket(self.request, server_side=True) as tls:
            self._handle(client=tls)
