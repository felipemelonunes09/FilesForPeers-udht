from injector import Injector
from core.DHTModule import DHTModule

global D_HASH_TABLE_NAME
D_HASH_TABLE_NAME = "data/duser-hash-table"

injector = Injector([DHTModule()])

CONSUMERS_QUANTITY = 4
HOST="127.0.0.1"
PORT=8000
BASIC_DECODER = 'utf-8'