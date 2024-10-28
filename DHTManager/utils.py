
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

def get_logger(name: str) -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = TimedRotatingFileHandler("logs/server.log", when="midnight", interval=1)
    handler.suffix = "%Y-%m-%d" 
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class Message():
    class MessageAction(Enum):
        ADD_PEER="peer add"
        REMOVE_PEER="peer remove"
        UPDATE_PEER="peer update"
        GET_PEER="peer get"
    class MessageResult(Enum):
        ERROR="error"    
        COMPLETED="completed"
    
    def __init__(self) -> None:
        self.action: Message.MessageAction = None
        self.result: Message.MessageResult = None
        self.data: dict = None
        
    def to_dict(self) -> dict[str, str]:
        return {
            "action": self.action.value,
            "result": self.result.value,
            "data": self.data
        }