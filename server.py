from server import server

import argparse

parser = argparse.ArgumentParser(
    description="Server of the Distributed Tic-Tac-Toe system"
)
parser.add_argument("port", type=int, help="the port of the host")
parser.add_argument("port_tls", type=int, help="the port of the host")

if __name__ == "__main__":
    args = parser.parse_args()
    server.run(args.port, args.port_tls)
