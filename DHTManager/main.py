import json
from typing import List

from utils import ClientState, ServerState, get_logger
from core.DHTService import DHTService
from core.Peer import Peer
from queue import Queue
from socket import *
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
        self.__queue:Queue[Peer.tuple] = Queue()
    
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
            try:
                data = connection.recv(1024)
                data = data.decode(globals.BASIC_DECODER)
                self.logger.info(f"(*) received {data} from {address}")
                data: dict = json.loads(data)
                message_type = int(data.get("message_type", -1))
                bdata = data.get("data", dict())
                
                if message_type != ClientState.CLOSE:   
                    self.__queue.put((message_type, bdata, address, connection))
                    self.logger.info(f"(*) {address} request code: {message_type} on queue")
                else:
                    alive=False
                    connection.close()
            except json.decoder.JSONDecodeError as e:
                alive=False
                connection.close

    def __create_consumers(self) -> None:
        def consumer() -> None:
            while True:
                message_type, data, address, connection = self.__queue.get()
                message = {}
                peer_ip = data.get("peer_ip", "")
                peer_name = data.get("peer_name", "")
                peer_port = data.get("peer_port", "")
                peer = Peer(ip=peer_ip, name=peer_name, port=peer_port)
                if message_type == 2:
                    self.logger.info(f"(*) {address} request: sending hash-table without code")
                    result = self.dht_service.get_hash_table()
                    connection.send(result)
                elif message_type == 4:
                    result = self.dht_service.remove_peer(peer_ip)
                    self.logger.info(f"(*) {address} request: removing peer result: {result} ")
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == 3:
                    result = self.dht_service.create_peer(peer)
                    self.logger.info(f"(*) {address} request: adding peer result: {result} ")
                    message['data'] = result
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == 7:
                    peer: Peer = self.dht_service.get_peer(peer_ip)
                    self.logger.info(f"(*) {address} request: getting peer result: {peer.to_tuple()} ")
                    message['data'] = peer
                    message = json.dumps(message).encode(globals.BASIC_DECODER)
                    connection.send(message)
                elif message_type == 6:
                    result = self.dht_service.update_peer(peer)
                    self.logger.info(f"(*) {address} request: updating peer result: {result}")
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