import json
from typing import List
from core.DHTService import DHTService
from core.Peer import Peer
from queue import Queue
from socket import *
from utils import ClientState, ServerState, get_logger
import threading
import globals

class Server:
    def __init__(self):
        self.logger = get_logger("ServerLogger")
        self.dht_service = globals.injector.get(DHTService)
        self.__client_list: List[threading.Thread] = list()
        self.__consumers_list: List[threading.Thread] = list()
        self.__consumers = globals.CONSUMERS_QUANTITY
        self.__server_address = (globals.HOST, globals.PORT)
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__queue = Queue()
    
    def start(self) -> None: 
        self.logger.info("(+) Server started.")
        self.__socket.bind(self.__server_address)
        self.__create_consumers()
        
        self.__socket.listen(10)
        
        while True:
            connection, address = self.__socket.accept()
            client_thread = threading.Thread(target=self.__handle_client, args=(connection, address))
            self.__client_list.append(client_thread)
            client_thread.start()
        
    def __handle_client(self, connection: socket, address: tuple) -> None:
        alive=True
        while alive:
            data = connection.recv(1024)
            data: dict = json.loads(data.decode(globals.BASIC_DECODER))
            message_type = data.get("message_type", ClientState.CLOSE)
            bdata = data.get("data", None)
            
            if message_type != ClientState.CLOSE:   
                self.__queue.put((message_type, bdata, address, connection))
            else:
                alive=False
                connection.close()

    def __create_consumers(self) -> None:
        def consumer() -> None:
            while True:
                message_type, data, address, connection = self.__queue.get()
                message_type:int
                data: dict
                adress: tuple
                connection: socket
                message = {}
                peer_ip = data.get("peer_ip", "")
                peer_name = data.get("peer_name", "")
                peer_port = data.get("peer_port", 0000)
                peer = Peer(name=peer_name, ip=peer_ip, port=peer_port)
                if message_type == ClientState.SEND_HASH_TABLE:
                    message['message_type'] = ServerState.SENDING_INFO
                    message['data'] = self.dht_service.get_hash_table()
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == ClientState.REMOVE_PEER:
                    result = self.dht_service.remove_peer(peer_ip)
                    message['message_type'] = ServerState.SENDING_INFO
                    message['data'] = result
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == ClientState.ADD_PEER:
                    result = self.dht_service.create_peer(peer)
                    message['data'] = result
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == ClientState.GET_PEER:
                    peer = self.dht_service.get_peer(peer_ip)
                    message['data'] = peer
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == ClientState.UPDATE_PEER:
                    result = self.dht_service.update_peer(peer)
                    message['data'] = result
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                
        for _ in range(self.__consumers):
            consumer_thread = threading.Thread(target=consumer)
            self.__consumers_list.append(consumer_thread)
            consumer_thread.start()
        

if __name__ == "__main__":
    server = Server()
    server.start()