
import json
from utils import get_logger
import pickle
from queue import Queue
from socket import *
import threading
from typing import List
import globals


class Server:
    class ClientState(Enum):
        CLOSE = 1
        RECEIVE_HASH_TABLE = 2
        SEND_HASH_TABLE = 3
    
    def  __init__(self, host: str, port: int, dht_manager_address: tuple):
        self.__host = host
        self.__port = port
        self.logger = get_logger("ServerLogger")
        self.__dht_manager_address = dht_manager_address
        self.__socket_manager = socket(AF_INET, SOCK_STREAM)
        self.__local_socket = socket(AF_INET, SOCK_STREAM)
        self.__peer_connections: List[threading.Thread] = []
        self.__in_memory_hash_table = {}
        self.__queue = Queue()
        self.__lock = threading.Lock()
        
    def start(self) -> None:
        self.__connect_to_manager()
        self.logger.info("DHTSync Started")
        
        try:
            self.__local_socket.bind((self.__host, self.__port))
            self.__local_socket.listen(socket.SOMAXCONN)
            while True:
                connection, address = self.__local_socket.accept()
                thread = threading.Thread(target=self.__handle_client_peer, args=(connection, address))
                self.__peer_connections.append(thread)
                thread.start()
        except Exception as e:
            self.logger.error(f"Error in local server: {e}")
        finally:
            self.__close()
            
    def __connect_to_manager(self):
        try:
            self.__socket_manager.connect(self.__dht_manager_address)
            self.logger.info(f"Connected to DHTManager at {self.__dht_manager_address}")
            self.__request_udht()
        except Exception as e:
            self.logger.error(f"Error connecting to DHTManager: {e}")
            self.__socket_manager.close()

    def __request_udht(self) -> dict:
        try:
            request = { 
                "message_type": 2,
                "data": {}
            }

            self.socket.sendall(json.dumps(request).encode(globals.BASIC_DECODER))

            response = self.__socket_manager.recv(1024)
            self.__in_memory_hash_table = pickle.loads(response)
            self.logger.info("Hash table has been received from DHTManager.")
        except Exception as e:
            self.logger.error(f"Error requesting hash table: {e}")
    
    def __handle_peer_connection(self, connection: socket, address: tuple, is_client=False) -> None:
        try:
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                response = response.decode(globals.BASIC_DECODER)
                self.logger.info(f"(*) received {data} from {address}")
                data: dict = json.loads(response)
                message_type = int(data.get("message_type", -1))
                
                if message_type == 2:
                    local_table = pickle.dumps(self.__in_memory_hash_table)
                elif message_type == 3:
                    peer_table = response.get("data", {})
                    self.__merge_tables(peer_table)
                
        except Exception as e:
            self.logger.error(f"Error handling peer {address}: {e}")

    #def __merge_tables():
    
    def __close(self):
        self.__local_socket.close()

if __name__ == "__main__":
    server = Server(
        host=globals.HOST,
        port=globals.PORT,
        dht_manager_address=(globals.DHT_MANAGER_HOST, globals.DHT_MANAGER_PORT)
    )
    server.start()