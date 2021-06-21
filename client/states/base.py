class State:
    def __init__(self, client) -> None:
        self.client = client

    def get_input_command(self):
        return input(f"JogoDaVelha> ").strip().split() or [""]

    def handle_input_command(self, *input_command):
        pass

    def handle_opponent_command(self, *command):
        pass

    def handle_new_connection_command(self, *command):
        pass

    def _handle_skip(self):
        pass

    def _handle_default(self, *args):
        print("Invalid command!")

    def _handle_exit(self):
        self.client.stop()
