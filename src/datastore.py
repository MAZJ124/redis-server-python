class DataStore:
    def __init__(self):
        self._data = dict()
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    