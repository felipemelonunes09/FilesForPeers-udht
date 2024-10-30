import json
from utils import ClientState, Message, get_logger
from core.DHTService import DHTService
from typing import List
from core.Peer import Peer
from queue import Queue
from socket import *
import threading
import globals

class Server:
    
    def __init__(self, port: int, host: str, dht_service: DHTService):
        print(port)
        print(host)
        self.logger = get_logger("ServerLogger")
        self.dht_service = dht_service
        self.__consumers = globals.CONSUMERS_QUANTITY
        self.__client_list: List[threading.Thread] = list()
        self.__consumers_list: List[threading.Thread] = list()
        self.__server_address = (host, port)
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__queue:Queue[Peer.ptuple] = Queue()
    
    def start(self) -> None: 
        self.logger.info("(+) Server started.")
        self.__socket.bind(self.__server_address)
        self.__create_consumers()
        self.__socket.listen(globals.SOCKETS_CONNECTION_LIMIT)
        
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
                connection.close()
                self.logger.error(f"Invalid JSON data received from {address}: {e}")
            except Exception as e:
                connection.close()
                alive = False
                self.logger.error(f"Unexpected error handling client {address}: {e}")
            
    def __create_consumers(self) -> None:
        def consumer() -> None:
            while True:
                message_type, data, address, connection = self.__queue.get()
                peer_ip = data.get("peer_ip", "")
                peer_name = data.get("peer_name", "")
                peer_port = data.get("peer_port", "")
                peer = Peer(ip=peer_ip, name=peer_name, port=peer_port)
                if message_type == ClientState.SEND_HASH_TABLE.value:
                    self.logger.info(f"(*) {address} request: sending hash-table without code")
                    result = self.dht_service.get_hash_table()
                    connection.sendall(result)
                else:
                    message = Message()
                    try:
                        result = False
                        if message_type == ClientState.REMOVE_PEER.value:
                            message.action = Message.MessageAction.REMOVE_PEER
                            result = self.dht_service.remove_peer(peer)
                            self.logger.info(f"(*) {address} request: removing peer result: {result} ")
                        elif message_type == ClientState.ADD_PEER.value:
                            message.action = Message.MessageAction.ADD_PEER
                            result = self.dht_service.create_peer(peer)
                            self.logger.info(f"(*) {address} request: adding peer result: {result} ")
                            message.data = result
                        elif message_type == ClientState.GET_PEER.value:
                            message.action = Message.MessageAction.GET_PEER
                            peer: dict[str, str] = self.dht_service.get_peer(peer_ip)
                            self.logger.info(f"(*) {address} request: getting peer result: {peer} ")
                            message.data = peer
                        elif message_type == ClientState.UPDATE_PEER.value:
                            message.action = Message.MessageAction.UPDATE_PEER
                            result = self.dht_service.update_peer(peer)
                            self.logger.info(f"(*) {address} request: updating peer result: {result}")
                            message.data = result
                        message.result = Message.MessageResult.COMPLETED if result else Message.MessageResult.ERROR
                    except Exception as e:
                        message.result = message.MessageResult.ERROR
                    message = json.dumps(message.to_dict()).encode(globals.BASIC_DECODER)
                    connection.sendall(message)
        for _ in range(self.__consumers):
            consumer_thread = threading.Thread(target=consumer)
            self.__consumers_list.append(consumer_thread)
            consumer_thread.start()

if __name__ == "__main__":
    server = Server(port=globals.PORT, host=globals.HOST, dht_service=globals.injector.get(DHTService))
    server.start()