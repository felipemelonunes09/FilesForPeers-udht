from datetime import datetime
from socket import socket
from typing import Dict, Union

class Peer:
    ptuple = tuple[int, dict, tuple, socket]
    def __init__(self, name: str, ip: str, port: int) -> None:
        self.name = name
        self.ip = ip
        self.port = port
        self.created_at = str(datetime.now())
        self.last_connection_on = str(datetime.now())
        
    def to_tuple(self) -> tuple[str, str, str, str, str]:
        return (self.name, self.ip, self.port, self.created_at, self.last_connection_on)
    
    def to_dict(self) -> Dict[str, Union[str, str]]:
        return {
            "name": self.name,
            "ip": self.ip,
            "port": self.port,
            "createdAt": self.created_at,
            "lastConnectionOn": self.last_connection_on
        }
