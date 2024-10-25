
from enum import Enum
import logging
from logging.handlers import TimedRotatingFileHandler
import os

class ClientState(Enum):
    CLOSE=1
    SEND_HASH_TABLE=2
    ADD_PEER=3
    REMOVE_PEER=4
    DELETE_PEER=5
    UPDATE_PEER=6
    GET_PEER=7
    
class ServerState(Enum):
    SENDING_INFO=1

def get_logger(name: str) -> None:
    os.makedirs("logs", exist_ok=True)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler("logs/server.log", when="midnight", interval=1)
    handler.suffix = "%Y-%m-%d" 
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger