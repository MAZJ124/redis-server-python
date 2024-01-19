from collections import deque
from dataclasses import dataclass
from itertools import islice
from random import sample
from threading import Lock
from time import time, time_ns

def to_ns(seconds):
    return seconds * 10**9

@dataclass
class DataEntry:
    value: any
    expiry: int = 0

    def __len__(self):
        return len(self.value)

class DataStore:
    def __init__(self):
        self._data = dict()
        self._lock = Lock()
    
    def __getitem__(self, key):
        with self._lock:
            entry = self._data[key]
            if entry.expiry and entry.expiry < time_ns():
                del self._data[key]
                raise KeyError
            return self._data[key].value
    
    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = DataEntry(value)

    def __contains__(self, key):
        with self._lock:
            return key in self._data
        
    def __delitem__(self, key):
        with self._lock:
            del self._data[key]

    def incr(self, key):
        with self._lock:
            entry = self._data.get(key, DataEntry(0))
            value = int(entry.value) + 1
            entry.value = str(value)
            self._data[key] = entry
        return value
    
    def decr(self, key):
        with self._lock:
            entry = self._data.get(key, DataEntry(0))
            value = int(entry.value) - 1
            entry.value = str(value)
            self._data[key] = entry
        return value
    
    def lpush(self, key, element):
        with self._lock:
            entry = self._data.get(key, DataEntry(deque()))
            if not isinstance(entry.value, deque):
                raise TypeError
            entry.value.appendleft(element)
            self._data[key] = entry
            return len(entry.value)
    
    def rpush(self, key, element):
        with self._lock:
            entry = self._data.get(key, DataEntry(deque()))
            if not isinstance(entry.value, deque):
                raise TypeError
            entry.value.append(element)
            self._data[key] = entry
            return len(entry.value)
        
    def lrange(self, key, start, end):
        with self._lock:
            entry = self._data.get(key, DataEntry(deque()))
            if not isinstance(entry.value, deque):
                raise TypeError
            length = len(entry.value)
            if start > length:
                return []
            if end > length:
                end = length
            if start < 0:
                start = max(length + start, 0)
            return list(islice(entry.value, start, end))

    def set_with_expiry(self, key, value, expiry):
        with self._lock:
            expiring_timestamp = time_ns() + to_ns(expiry)
            self._data[key] = DataEntry(value, expiring_timestamp)

    def auto_check_expiry(self):
        while True:
            try:
                keys = sample(list(self._data.keys()), 20)
            # when sample size is larger than sequence size, aka <20 keys stored
            except ValueError:
                return 
            expired_count = 0
            keys_count = len(keys)
            for key in keys:
                try:
                    with self._lock:
                        item = self._data[key]
                        if item.expiry and item.expiry < time_ns():
                            del self._data[key]
                            expired_count += 1
                except KeyError:
                    pass
            expired_ratio = expired_count / keys_count
            if expired_count <= 0.25:
                break 
