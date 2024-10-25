from injector import Injector
from core.DHTModule import DHTModule

global D_HASH_TABLE_NAME
D_HASH_TABLE_NAME = "data/duser-hash-table"

injector = Injector([DHTModule()])