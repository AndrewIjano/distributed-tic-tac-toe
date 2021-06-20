from server.models.base import BaseModel


class User(BaseModel):
    def __init__(
        self,
        username: str,
        password: str,
        is_active: bool = False,
        is_free: bool = True,
        host: str = "",
        port: str = "",
        points: int = 0,
    ) -> None:
        super().__init__()

        self.username = username
        self.password = password
        self.is_active = is_active
        self.is_free = is_free
        self.host = host
        self.port = port
        self.points = points


    @property
    def key(self):
        return self.username
