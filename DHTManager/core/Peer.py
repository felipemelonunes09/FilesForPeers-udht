from datetime import datetime

class Peer:
    def __init__(self, name: str, ip: str, port: int) -> None:
        self.name = name
        self.ip = ip
        self.port = port
        self.created_at = datetime.now()
        self.last_connection_on = datetime.now()
