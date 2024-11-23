from enum import Enum
import logging
from logging.handlers import TimedRotatingFileHandler
import os

def get_logger(name: str = "DHTSync") -> logging.Logger:
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = TimedRotatingFileHandler("logs/dhtsync.log", when="midnight", interval=1)
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger