from enum import Enum


class Command(Enum):
    ADD_USER = "adduser"
    LIST = "list"
    LOGIN = "login"
    LOGOUT = "logout"
    BEGIN = "begin"
    SEND = "send"
    END = "end"
    EXIT = "exit"
    DEFAULT = "default"
    SKIP = ""

    @classmethod
    def _missing_(cls, value):
        return Command.DEFAULT
