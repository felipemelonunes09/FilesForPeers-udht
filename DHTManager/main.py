from logging.handlers import TimedRotatingFileHandler
from typing import List
from core.DHTService import DHTService
from core.Peer import Peer
from queue import Queue
from socket import *
import threading
import logging
import globals
import os

class Server:
    def __init__(self):
        self.logger = self.setup_logger()
        self.dht_service = globals.injector.get(DHTService)
        self.__receiver_list: List[threading.Thread] = list()
        self.__consumer_list: List[threading.Thread] = list()
        self.__consumers: int = globals.CONSUMERS_QUANTITY
        self.__receivers: int = globals.RECEIVERS_QUANTITY
        self.__queue = Queue()
        self.__server_address = (globals.HOST, globals.PORT)
        self.__socket = socket(AF_INET, SOCK_STREAM)
        
        
        
    def setup_logger(self):
        os.makedirs("logs", exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger("ServerLogger")
        logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler("logs/server.log", when="midnight", interval=1)
        handler.suffix = "%Y-%m-%d" 
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def start(self):
        
        self.logger.info("Server started.")
        self.__socket.bind(self.__server_address)
        
        def receiver():
            while True:
                pass
        
        def consumer():
            while True:
                pass
            
        for _ in range(self.receivers):
            receive_message_thread = threading.Thread(target=receiver, args=())
            receive_message_thread.start()
            self.__receiver_list.append(receive_message_thread)
        
        for _ in range(self.__consumers):
            receive_message_thread = threading.Thread(target=receiver, args=())
            receive_message_thread.start()
            self.__receiver_list.append(receive_message_thread)
            
        
            

if __name__ == "__main__":
    server = Server()
    server.start()
