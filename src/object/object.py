import uuid

class Object:
    def __init__(self) -> None:
        self.uuid = uuid.uuid1()