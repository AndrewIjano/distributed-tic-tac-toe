from typing import Callable, List, Union
from server.models.base import BaseModel

import json

# TODO: implement mutex


class DatabaseAdapter:
    def __init__(self, model_name: str) -> None:
        self.path = f"db/{model_name}.json"
        self._initialize_db()

    def _initialize_db(self):
        with open(self.path, "a+") as f:
            f.seek(0)
            if f.read(1) == "":
                f.write("{}")

    def create(self, item: BaseModel) -> None:
        with open(self.path, "r+") as file:
            items = self._get_items(file)
            items[item.key] = item.serialize()
            self._set_items(file, items)

    def read_one(self, key: str, Model: Callable[..., BaseModel]) -> BaseModel:
        with open(self.path, "r") as file:
            items = self._get_items(file)
            return Model(**items.get(key))

    def read_many(self, key_name: str, key_value: str, Model: Callable[..., BaseModel]):
        with open(self.path, "r") as file:
            items = self._get_items(file)
            return [
                Model(**item) for item in items.values() if item[key_name] == key_value
            ]

    def read_all(self, Model: Callable[..., BaseModel]) -> List[BaseModel]:
        with open(self.path, "r") as file:
            items = self._get_items(file)
            return [Model(**item) for item in items.values()]

    def update_one(
        self, key: str, update_key: str, update_value: Union[str, bool]
    ) -> BaseModel:
        with open(self.path, "r+") as file:
            items = self._get_items(file)
            item = items.get(key)
            item[update_key] = update_value
            items[key] = item
            self._set_items(file, items)

    @staticmethod
    def _get_items(file):
        return json.loads(file.read())

    @staticmethod
    def _set_items(file, items):
        file.seek(0)
        file.truncate()
        file.write(json.dumps(items))
