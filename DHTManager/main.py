from logging.handlers import TimedRotatingFileHandler
from core.DHTService import DHTService
import logging
import globals
import os

class Server:
    def __init__(self):
        self.logger = self.setup_logger()
        self.dht_service = globals.injector.get(DHTService)

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
        self.dht_service.create_peer(None)
        self.logger.info("Server started.")

if __name__ == "__main__":
    server = Server()
    server.start()
