
import json
import pickle
from socket import *
import threading
from typing import List
import globals


class Server:
    
    def  __init__(self):
        self.__dht_manager_address = (globals.DHT_MANAGER_HOST, globals.DHT_MANAGER_PORT)
        self.__server_address = (globals.HOST, globals.PORT)
        self.__socket = socket(AF_INET, SOCK_RAW)
        self.__socketDHTManager = socket(AF_INET, SOCK_STREAM)
        self.__in_memory_hash_table = dict()
        self.__client_list : List[threading.Thread] = list() 
        
    def start(self) -> None:
        self.__socketDHTManager.connect((self.__dht_manager_address))
        self.__in_memory_hash_table = self.__request_udht(self)
        self.__socket.bind(self.__server_address)
        self.__close()
        
        while True:
            connection , address = self.__socket.accept()
            client_thread = threading.Thread(target=self.__handle_client, args=(connection, address))
            self.__client_list.append(client_thread)
            client_thread.start()
            

    def __request_udht(self) -> dict:
        request = { 
            "message_type": 2,
            "data": {}
        }

        self.socket.sendall(json.dumps(request).encode(globals.BASIC_DECODER))

        response = self.socket.recv(1024)
        return pickle.loads(response)
    
    def __handle_client(self, connection: socket, address: tuple) -> None:
        while True:
            response = connection.recv(1024)
            response = response.decode(globals.BASIC_DECODER)
            data: dict = json.loads(response)
            


    
    def __close(self):
        self.socket.close()

if __name__ == "__main__":
    server = Server()
    server.start()