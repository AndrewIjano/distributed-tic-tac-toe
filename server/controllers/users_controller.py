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

    def get_active_users(self) -> List[User]:
        return self.db.read_many(key_name="is_active", key_value=True, Model=User)

    def set_user_active(self, username: str):
        self.db.update_one(key=username, update_key="is_active", update_value=True)

    def set_user_inactive(self, username: str):
        self.db.update_one(key=username, update_key="is_active", update_value=False)

    def update_user_address(self, username, host, port):
        self.db.update_one(key=username, update_key="host", update_value=host)
        self.db.update_one(key=username, update_key="port", update_value=port)
