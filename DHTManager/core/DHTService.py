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
        print("peer created")
        pass
    
    def update_peer(self, peer: Peer) -> bool:
        pass
    
    def remove_peer(self, peer: Peer) -> bool:
        pass
    
    def get_peer(self) -> Peer | None:
        pass
    
    def get_hash_table(self) -> DHT:
        pass