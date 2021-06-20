from client import client

import argparse

parser = argparse.ArgumentParser(
    description="Client of the Distributed Tic-Tac-Toe system"
)
parser.add_argument("host", type=str, help="the IP address of the host")
parser.add_argument("port", type=int, help="the port of the host")
parser.add_argument("port_tls", type=int, help="the port of the host")


if __name__ == "__main__":
    args = parser.parse_args()
    client.run(server_host=args.host, server_port=args.port, server_port_tls=args.port_tls)
