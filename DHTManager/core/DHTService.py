from core.DHT import DHT
from core.Peer import Peer
from injector import inject
from singleton_decorator import singleton

@singleton
class DHTService:
    @inject
    def __init__(self, dht: DHT) -> None:
        self.__dhash_table = dht
        
    def create_peer(self, peer: Peer) -> bool:
        registry = self.__dhash_table.get(peer.ip, None)
        if not registry:
            self.__dhash_table[peer.ip] = peer 
            return True
        return False
    
    def update_peer(self, peer: Peer) -> bool:
        registry = self.__dhash_table.get(peer.ip, None)
        if registry:
            self.__dhash_table[peer.ip] = peer
            return True
        return False
    
    def remove_peer(self, peer: Peer) -> bool:
        registry = self.__dhash_table.get(peer.ip, None)
        if registry:
            self.__dhash_table[peer.ip] = None
            del self.__dhash_table
            return True
        return False
    
    def get_peer(self, ip: str) -> Peer | None:
        return self.__dhash_table.get(ip, None)
    
    def get_hash_table(self) -> DHT:
        ...