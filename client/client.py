from client.dt3p_adapter import Dt3pAdapter
from client.commands import Command


def run(host, port):
    server = Dt3pAdapter(host, port)
    while True:
        cmd = _get_cmd()

        command, *args = cmd.split()
        if command == Command.ADD_USER.value:
            user, password = args
            server.add_user(user, password)
        if command == Command.END.value:
            break


def _get_cmd():
    return input("JogoDaVelha> ")
