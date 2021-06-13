from typing import List
from server.db import DatabaseAdapter
from server.models.user import User


class UsersController:
    def __init__(self) -> None:
        self.db = DatabaseAdapter("users")

    def add_user(self, username: str, password: str):
        user = User(username, password)
        self.db.create(user)

    def get_user(self, username: str) -> User:
        return self.db.read_one(key=username, Model=User)

    def get_users(self) -> List[User]:
        return self.db.read_all(Model=User)
