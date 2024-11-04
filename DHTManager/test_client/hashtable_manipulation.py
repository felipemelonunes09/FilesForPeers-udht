import os
from socket import *
import json
import threading
import sys

class Client():
    
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        
        self.host = '127.0.0.1'
        self.port = 8000 
        self.address = (self.host, self.port)
        
        self.encoding = 'utf-8'
        data = {
            "message_type": 7,
            "data": {
                "peer_ip": "101.3.4.2",
                "peer_port": "8001",
                "peer_name": "Felipe Nunes"
            }
        }
        
        self.socket.connect(self.address)
        self.socket.send(json.dumps(data).encode("utf-8"))
        data = self.socket.recv(1024)
        print(data)
        print(json.loads(data.decode("utf-8")))
        
if __name__ == "__main__":
    client = Client()