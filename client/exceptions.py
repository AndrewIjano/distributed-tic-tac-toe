class UserNotActive(Exception):
    def __init__(self) -> None:
        pass

class MoveOutOfBounds(Exception):
    def __init__(self) -> None:
        pass

class MoveAlreadyDone(Exception):
    def __init__(self) -> None:
        pass
