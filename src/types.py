from dataclasses import dataclass
from collections.abc import Sequence

@dataclass
class SimpleString:
    data: str
    def __eq__(self, other):
        return self.data == other.data

@dataclass
class Error:
    data: str
    def __eq__(self, other):
        return self.data == other.data

@dataclass
class Integer:
    value: int
    def __eq__(self, other):
        return self.value == other.value

@dataclass
class BulkString:
    data: bytes
    def __eq__(self, other):
        return self.data == other.data

@dataclass
class Array(Sequence):
    data: list
    def __eq__(self, other):
        return self.data == other.data

    def __getitem__(self, i):
        return self.data[i]

    def __len__(self):
        return len(self.data)
