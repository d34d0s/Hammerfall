from .globs import pg

class HFProc:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def callback(self, data) -> bool: raise NotImplementedError
    def fallback(self, data) -> bool: raise NotImplementedError
