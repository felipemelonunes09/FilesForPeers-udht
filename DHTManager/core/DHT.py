import shelve

class DHT(shelve.DbfilenameShelf):
    def __init__(self, filename, default_factory=None, **kwargs):
        super().__init__(filename, **kwargs)
        self.default_factory = default_factory 

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            if self.default_factory is None:
                raise
            else:
                value = self.default_factory()
                self[key] = value  
                return value