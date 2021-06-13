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
        if command == Command.LOGIN.value:
            user, password = args
            server.login(user, password)
        if command == Command.LIST.value:
            active_users = server.list_active_users()
            print("status | username")
            print("-----------------")
            print("\n".join(f"  {status}   {user}" for user, status in active_users))
        if command == Command.END.value:
            break


def _get_cmd():
    return input("JogoDaVelha> ")
