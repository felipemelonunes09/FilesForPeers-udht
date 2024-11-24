
from datetime import datetime
from enum import Enum
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
        SEND_HASH_TABLE = 2
        RECEIVE_HASH_TABLE = 3
    
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

            self.__socket_manager.sendall(json.dumps(request).encode(globals.BASIC_DECODER))

            response = self.__socket_manager.recv(1024)
            self.__in_memory_hash_table = pickle.loads(response)
            self.logger.info("Hash table has been received from DHTManager.")
        except Exception as e:
            self.logger.error(f"Error requesting hash table: {e}")
    
    def __handle_client_peer(self, connection: socket, address: tuple, is_client=False) -> None:
        try:
            is_synced = False
            
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                
                decoded_data = data.decode(globals.BASIC_DECODER)
                self.logger.info(f"(*) received {data} from {address}")
                request: dict = json.loads(decoded_data)
                message_type = int(request.get("message_type", -1))
                
                if message_type == self.ClientState.RECEIVE_HASH_TABLE.value:
                    peer_table = pickle.loads(request.get("data", b""))
                    self.__merge_tables(peer_table)
                    
                    if not is_synced:
                        local_table = pickle.dumps(self.__in_memory_hash_table)
                        response = {
                            "message_type": self.ClientState.SEND_HASH_TABLE.value,
                            "data": local_table
                        }
                        connection.sendall(json.dumps(response).encode(globals.BASIC_DECODER))
                        is_synced = True
                    
                elif message_type == self.ClientState.SEND_HASH_TABLE.value:
                    local_table = pickle.dumps(self.__in_memory_hash_table)
                    
                    response = {
                        "message_type": self.ClientState.RECEIVE_HASH_TABLE.value,
                        "data": local_table
                    }
                    
                    connection.sendall(json.dumps(response).encode(globals.BASIC_DECODER))

                    peer_table = pickle.loads(request.get("data", b""))
                    self.__merge_tables(peer_table)
                    is_synced = True
                
        except Exception as e:
            self.logger.error(f"Error handling peer {address}: {e}")

    def __merge_tables(self, peer_table: dict) -> None:
        with self.__lock:
            local_tokens = set(self.__in_memory_hash_table.keys())
            peer_tokens = set(peer_table.keys())
            new_tokens = peer_tokens - local_tokens
            conflicting_tokens = local_tokens & peer_tokens
            
            for token in new_tokens:
                self.__in_memory_hash_table[token] = peer_table[token]
                self.logger.info(f"Added new token {token} to the hash table.")
            
            for token in conflicting_tokens:
                local_data = self.__in_memory_hash_table[token]
                peer_data = peer_table[token]
                if self.__should_update(local_data, peer_data):
                    self.__in_memory_hash_table[token] = peer_data
                    self.logger.info(f"Updated token {token} in the hash table.")

    def __should_update(self, local_data: dict, remote_data: dict) -> bool:       
        local_timestamp = local_data.get("updatedAt")
        remote_timestamp = remote_data.get("updatedAt")
        
        if not local_timestamp or not remote_timestamp:
            self.logger.warning(f"Missing 'updatedAt' for token. Skipping update.")
            return False
        try:
            local_time = datetime.fromisoformat(local_timestamp)
            remote_time = datetime.fromisoformat(remote_timestamp)
            return remote_time > local_time 
        except ValueError as e:
            self.logger.error(f"Invalid timestamp format: {e}")
            return False
            
    def __close(self):
        self.__local_socket.close()

if __name__ == "__main__":
    server = Server(
        host=globals.HOST,
        port=globals.PORT,
        dht_manager_address=(globals.DHT_MANAGER_HOST, globals.DHT_MANAGER_PORT)
    )
    server.start()