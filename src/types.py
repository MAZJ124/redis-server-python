from dataclasses import dataclass
from collections.abc import Sequence

@dataclass
class SimpleString:
    data: str
    def __eq__(self, other):
        return self.data == other.data
    
    def as_str(self):
        return self.data
    
    def resp_encode(self):
        return f'+{self.data}\r\n'.encode()

@dataclass
class Error:
    data: str
    def __eq__(self, other):
        return self.data == other.data
    
    def as_str(self):
        return self.data
    
    def resp_encode(self):
        return f'-{self.data}\r\n'.encode()

@dataclass
class Integer:
    value: int
    def __eq__(self, other):
        return self.value == other.value
    
    def as_str(self):
        return str(self.value)
    
    def resp_encode(self):
        return f':{self.value}\r\n'.encode()

@dataclass
class BulkString:
    data: bytes
    def __eq__(self, other):
        return self.data == other.data
    
    def as_str(self):
        return self.data.decode()
    
    def resp_encode(self):
        if self.data is None:
            return '$-1\r\n'.encode()
        return f'${len(self.data)}\r\n{self.data}\r\n'.encode()

@dataclass
class Array(Sequence):
    data: list
    def __eq__(self, other):
        return self.data == other.data

    def __getitem__(self, i):
        return self.data[i]

    def __len__(self):
        return len(self.data)
    
    def resp_encode(self):
        if self.data is None:
            return '*-1\r\n'.encode()
        array_length = len(self.data)
        encoded_message = [f'*{array_length}\r\n'.encode()]
        for i in range(array_length):
            encoded_element = self.data[i].resp_encode()
            encoded_message.append(encoded_element)
        return b''.join(encoded_message)
