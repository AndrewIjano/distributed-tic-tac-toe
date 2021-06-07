from server import server

import argparse

parser = argparse.ArgumentParser(
    description="Server of the Distributed Tic-Tac-Toe system"
)

if __name__ == "__main__":
    server.main()
