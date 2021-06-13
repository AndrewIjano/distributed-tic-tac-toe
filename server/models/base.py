class BaseModel:
    @property
    def key(self):
        raise NotImplementedError()

    def serialize(self):
        return vars(self)
