from dataclasses import dataclass
from src.types import (
    Array,
    BulkString,
    Error,
    Integer,
    SimpleString,
)

SEPERATOR = b'\r\n'
SEPERATOR_SIZE = len(SEPERATOR)

def extract_frame_from_buffer(buffer):
    seperator_index = buffer.find(SEPERATOR)
    if seperator_index == -1:
        return None, 0
    payload = buffer[1: seperator_index].decode()
    match chr(buffer[0]):
        case '+':
            return SimpleString(payload), seperator_index + SEPERATOR_SIZE
        case '-':
            return Error(payload), seperator_index + SEPERATOR_SIZE
        case ':':
            return Integer(int(payload)), seperator_index + SEPERATOR_SIZE
        case '$':
            length = int(payload)
            if length == -1:
                return BulkString(None), 5
            start_index = seperator_index + SEPERATOR_SIZE
            end_index = start_index + length
            payload = buffer[start_index:end_index]
            if len(buffer) < seperator_index + SEPERATOR_SIZE + length + SEPERATOR_SIZE:
                return None, 0
            return BulkString(payload), seperator_index + SEPERATOR_SIZE + length + SEPERATOR_SIZE
        case '*':
            length = int(payload)
            if length == 0:
                return Array([]), seperator_index + SEPERATOR_SIZE
            if length == -1:
                return Array(None), seperator_index + SEPERATOR_SIZE
            array = []
            for _ in range(length):
                next_item, length = extract_frame_from_buffer(buffer[seperator_index + SEPERATOR_SIZE:])
                if next_item and length:
                    array.append(next_item)
                    seperator_index += length
                else:
                    return None, 0
            return Array(array), seperator_index + SEPERATOR_SIZE
        case _:
            return None, 0
        
def encode_message(message):
    return message.resp_encode()
