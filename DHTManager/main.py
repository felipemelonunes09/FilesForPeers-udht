import json
from utils import get_logger
from core.DHTService import DHTService
from typing import List
from core.Peer import Peer
from queue import Queue
from socket import *
import threading
import globals

from enum import Enum

class Server:
    class ClientState(Enum):
        CLOSE=1
        SEND_HASH_TABLE=2
        ADD_PEER=3
        REMOVE_PEER=4
        DELETE_PEER=5
        UPDATE_PEER=6
        GET_PEER=7
        
    class ServerMessage():
        class MessageAction(Enum):
            ADD_PEER="peer add"
            REMOVE_PEER="peer remove"
            UPDATE_PEER="peer update"
            GET_PEER="peer get"
        class MessageResult(Enum):
            ERROR="error"    
            COMPLETED="completed"
        
        def __init__(self) -> None:
            self.action: Server.ServerMessage.MessageAction = None
            self.result: Server.ServerMessage.MessageResult = None
            self.data: dict = None
            
        def to_dict(self) -> dict[str, str]:
            return { "action": self.action.value, "result": self.result.value,"data": self.data  }
    
    def __init__(self, port: int, host: str, dht_service: DHTService):
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
                if len(data) > 2:
                    self.logger.info(f"(*) received {data} from {address}")
                    data: dict = json.loads(data)
                    message_type = int(data.get("message_type", -1))
                    bdata = data.get("data", dict())
                    if message_type != Server.ClientState.CLOSE:   
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
                if message_type == Server.ClientState.SEND_HASH_TABLE.value:
                    self.logger.info(f"(*) {address} request: sending hash-table without code")
                    result = self.dht_service.get_hash_table()
                    connection.sendall(result)
                else:
                    message = Server.ServerMessage()
                    try:
                        result = False
                        if message_type == Server.ClientState.REMOVE_PEER.value:
                            message.action = Server.ServerMessage.MessageAction.REMOVE_PEER
                            result = self.dht_service.remove_peer(peer)
                            self.logger.info(f"(*) {address} request: removing peer result: {result} ")
                        elif message_type == Server.ClientState.ADD_PEER.value:
                            message.action = Server.ServerMessage.MessageAction.ADD_PEER
                            result = self.dht_service.create_peer(peer)
                            self.logger.info(f"(*) {address} request: adding peer result: {result} ")
                            message.data = result
                        elif message_type == Server.ClientState.GET_PEER.value:
                            message.action = Server.ServerMessage.MessageAction.GET_PEER
                            result: dict[str, str] = self.dht_service.get_peer(peer_ip)
                            self.logger.info(f"(*) {address} request: getting peer result: {peer} ")
                            message.data = result
                        elif message_type == Server.ClientState.UPDATE_PEER.value:
                            message.action = Server.ServerMessage.MessageAction.UPDATE_PEER
                            result = self.dht_service.update_peer(peer)
                            self.logger.info(f"(*) {address} request: updating peer result: {result}")
                            message.data = result
                        message.result = Server.ServerMessage.MessageResult.COMPLETED if result else Server.ServerMessage.MessageResult.ERROR
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