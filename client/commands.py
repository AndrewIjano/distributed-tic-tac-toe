from enum import Enum


class Command(Enum):
    ADD_USER = "adduser"
    PASSWORD = "passwd"
    LIST = "list"
    LEADERS = "leaders"
    LOGIN = "login"
    LOGOUT = "logout"
    BEGIN = "begin"
    SEND = "send"
    DELAY = "delay"
    END = "end"
    EXIT = "exit"
    DEFAULT = "default"
    SKIP = ""

    @classmethod
    def _missing_(cls, value):
        return Command.DEFAULT
