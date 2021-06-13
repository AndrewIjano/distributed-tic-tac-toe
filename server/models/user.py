from server.models.base import BaseModel


class User(BaseModel):
    def __init__(self, username: str, password: str) -> None:
        super().__init__()

        self.username = username
        self.password = password

    @property
    def key(self):
        return self.username
