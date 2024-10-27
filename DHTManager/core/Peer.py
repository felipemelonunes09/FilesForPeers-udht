from datetime import datetime
from socket import socket

class Peer:
    
    tuple = tuple[int, dict, tuple, socket]
    def __init__(self, name: str, ip: str, port: int) -> None:
        self.name = name
        self.ip = ip
        self.port = port
        self.created_at = datetime.now()
        self.last_connection_on = datetime.now()
        
    def to_tuple(self) -> tuple[str, str, str, datetime, datetime]:
        return (self.name, self.ip, self.port, self.created_at, self.last_connection_on)
