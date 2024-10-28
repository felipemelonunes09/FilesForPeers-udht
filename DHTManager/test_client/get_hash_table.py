from socket import *
import json
import pickle

class Client():
    
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        
        self.host = '127.0.0.1'
        self.port = 8000 
        self.address = (self.host, self.port)
        
        self.encoding = 'utf-8'
        data = {
            'message_type': 2
        }
        
        self.socket.connect(self.address)
        self.socket.send(json.dumps(data).encode("utf-8"))
        data = self.socket.recv(1024)
        
        _ = pickle.loads(data)

        print(_)
        
if __name__ == "__main__":
    client = Client()