from injector import Injector, inject, Module, provider
from core.DHT import DHT
from core.Peer import Peer
from core.DHTService import DHTService
import globals

class DHTModule(Module):
    @provider
    def provide_dht(self) -> DHT:
        return DHT(globals.D_HASH_TABLE_NAME, default_factory=Peer)
    
    @provider
    def provide_dht_service(self, dht: DHT) -> DHTService:
        return DHTService(dht)