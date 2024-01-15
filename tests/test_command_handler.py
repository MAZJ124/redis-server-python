import pytest
from src.command_handler import handle_command
from src.datastore import DataStore
from src.types import Array, BulkString, Error, Integer, SimpleString

@pytest.mark.parametrize(
    "command, expected",
    [
        # Echo Tests
        (
            Array([BulkString(b"ECHO")]),
            Error("ERR wrong number of arguments for ECHO command"),
        ),
        (Array([BulkString(b"echo"), BulkString(b"Hello")]), BulkString("Hello")),
        (
            Array([BulkString(b"echo"), BulkString(b"Hello"), BulkString("World")]),
            Error("ERR wrong number of arguments for ECHO command"),
        ),
        # Ping Tests
        (Array([BulkString(b"ping")]), SimpleString("PONG")),
        (Array([BulkString(b"ping"), BulkString(b"Hello")]), BulkString("Hello")),
        (
            Array([BulkString(b"ping"), BulkString(b"Hello"), BulkString("Hello")]),
            Error("ERR wrong number of arguments for PING command"),
        ),
        # Set Command Tests 
        (
            Array([BulkString(b"set")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array([BulkString(b"set"), SimpleString(b"key")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array([BulkString(b"set"), SimpleString(b"key"), SimpleString(b"value")]),
            SimpleString("OK"),
        ),
        # Get Command Tests
        (
            Array([BulkString(b"get")]),
            Error("ERR wrong number of arguments for 'get' command"),
        ),
    ],
)

def test_handle_command(command, expected):
    datastore = DataStore()
    result = handle_command(command, datastore)
    assert result == expected
