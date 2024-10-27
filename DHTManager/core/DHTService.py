from core.Peer import Peer
from injector import inject
from singleton_decorator import singleton
from datetime import datetime
import shelve
import pickle

@singleton
class DHTService:
    @inject
    def __init__(self, filename: str) -> None:
        self.__filename = filename
        
    def create_peer(self, peer: Peer) -> bool:     
        with shelve.open(self.__filename) as hash_table:
            registry = hash_table.get(peer.ip, None)
            if not registry:
                hash_table[peer.ip] = peer.to_tuple()
                return True
        return False
    
    def update_peer(self, peer: Peer) -> bool:
        with shelve.open(self.__filename) as hash_table:
            registry = hash_table.get(peer.ip, None)
            if registry:
                hash_table[peer.ip] = peer.to_tuple()
                return True
        return False
    
    def remove_peer(self, peer: Peer) -> bool:
        
        with shelve.open(self.__filename) as hash_table:
            registry = hash_table.get(peer.ip, None)
            if registry:
                hash_table[peer.ip] = None
                del hash_table[peer.ip]
                return True
        return False
    
    def get_peer(self, ip: str) -> Peer | None:
        return self.__dhash_table.get(ip, None)
    
    def get_hash_table(self) -> bytes:
        hash_table_copy = dict()
        with shelve.open(self.__filename) as hash_table:  
            hash_table_copy = pickle.dumps(dict(hash_table))
        return hash_table_copy