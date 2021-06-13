from server import server

# HOST = "127.0.0.1"
# PORT = 65432

import argparse

parser = argparse.ArgumentParser(
    description="Server of the Distributed Tic-Tac-Toe system"
)
parser.add_argument("host", type=str, help="the IP address of the host")
parser.add_argument("port", type=int, help="the port of the host")

if __name__ == "__main__":
    args = parser.parse_args()
    server.run(args.host, args.port)
