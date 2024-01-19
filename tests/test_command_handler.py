from time import sleep, time_ns
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
        # Set with Expire Errors
        (
            Array([BulkString(b"set"), SimpleString(b"key"), SimpleString(b"value"), SimpleString(b"ex")]),
            Error("ERR syntax error"),
        ),
        (
            Array([BulkString(b"set"), SimpleString(b"key"), SimpleString(b"value"), SimpleString(b"px")]),
            Error("ERR syntax error"),
        ),
        (
            Array([BulkString(b"set"), SimpleString(b"key"), SimpleString(b"value"), SimpleString(b"foo")]),
            Error("ERR syntax error"),
        ),
         # Exists Tests
        (
            Array([BulkString(b"exists")]),
            Error("ERR wrong number of arguments for 'exists' command"),
        ),
    ],
)

def test_handle_command(command, expected):
    datastore = DataStore()
    result = handle_command(command, datastore)
    assert result == expected

def test_set_with_expiry():
    datastore = DataStore()
    key = 'key'
    value = 'value'
    ex = 1
    px = 100

    base_command = [BulkString(b"set"), SimpleString(b"key"), SimpleString(b"value")]

    # seconds
    command = base_command[:]
    command.extend([BulkString(b"ex"), BulkString(f"{ex}".encode())])
    expected_expiry = time_ns() + (ex * 10**9)
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    stored = datastore._data[key]
    assert stored.value == value
    diff = - expected_expiry - stored.expiry
    assert diff < 10000

    # milliseconds
    command = base_command[:]
    command.extend([BulkString(b"px"), BulkString(f"{px}".encode())])
    expected_expiry = time_ns() + (ex * 10**6)
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    stored = datastore._data[key]
    assert stored.value == value
    diff = - expected_expiry - stored.expiry
    assert diff < 10000


def test_get_with_expiry():
    datastore = DataStore()
    key = 'key'
    value = 'value'
    px = 100

    command = [
        BulkString(b"set"),
        SimpleString(b"key"),
        SimpleString(b"value"),
        BulkString(b"px"),
        BulkString(f"{px}".encode())
    ]
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    sleep((px + 100)/1000)
    command = [BulkString(b"get"), SimpleString(b"key")]
    result = handle_command(command, datastore)
    assert result == BulkString(None)

# Incr Tests
def test_handle_incr_command_valid_key():
    datastore = DataStore()
    result = handle_command(Array([BulkString(b"incr"), SimpleString(b"ki")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([BulkString(b"incr"), SimpleString(b"ki")]), datastore)
    assert result == Integer(2)


# Decr Tests
def test_handle_decr():
    datastore = DataStore()
    result = handle_command(Array([BulkString(b"incr"), SimpleString(b"kd")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([BulkString(b"incr"), SimpleString(b"kd")]), datastore)
    assert result == Integer(2)
    result = handle_command(Array([BulkString(b"decr"), SimpleString(b"kd")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([BulkString(b"decr"), SimpleString(b"kd")]), datastore)
    assert result == Integer(0)

# Lpush Tests
def test_handle_lpush_lrange():
    datastore = DataStore()
    result = handle_command(Array([BulkString(b"lpush"), SimpleString(b"klp"), SimpleString(b"second")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([BulkString(b"lpush"), SimpleString(b"klp"), SimpleString(b"first")]), datastore)
    assert result == Integer(2)
    result = handle_command(Array([BulkString(b"lrange"), SimpleString(b"klp"), BulkString(b"0"), BulkString(b"2")]), datastore)
    assert result == Array(data=[BulkString("first"), BulkString("second")])

# Rpush Tests
def test_handle_rpush_lrange():
    datastore = DataStore()
    result = handle_command(Array([BulkString(b"rpush"), SimpleString(b"krp"), SimpleString(b"first")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([BulkString(b"rpush"), SimpleString(b"krp"), SimpleString(b"second")]), datastore)
    assert result == Integer(2)
    result = handle_command(Array([BulkString(b"lrange"), SimpleString(b"krp"), BulkString(b"0"), BulkString(b"2")]), datastore)
    assert result == Array(data=[BulkString("first"), BulkString("second")])
