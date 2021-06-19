from enum import Enum


class Command(Enum):
    ADD_USER = "adduser"
    LIST = "list"
    LOGIN = "login"
    LOGOUT = "logout"
    BEGIN = "begin"
    END = "end"
    EXIT = "exit"
