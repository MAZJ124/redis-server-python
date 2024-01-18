from src.types import Array, BulkString, Error, Integer, SimpleString

def _handle_echo(command):
    if len(command) == 2:
        message = command[1].data.decode()
        return BulkString(f'{message}')
    return Error('ERR wrong number of arguments for ECHO command')

def _handle_ping(command):
    if len(command) == 1:
        return SimpleString('PONG')
    if len(command) == 2:
        message = command[1].data.decode()
        return BulkString(f'{message}')
    return Error('ERR wrong number of arguments for PING command')

def _handle_set(command, datastore):
    if len(command) >= 3:
        key, value = command[1].data.decode(), command[2].data.decode()
        if len(command) == 3:
            datastore[key] = value
            return SimpleString('OK')
        elif len(command) == 5:
            expiry_mode = command[3].data.decode().upper()
            try:
                expiry = int(command[4].data.decode())
            except ValueError:
                return Error('ERR value is not an integer or out of range')
            match expiry_mode:
                case 'EX':
                    datastore.set_with_expiry(key, value, expiry)
                    return SimpleString('OK')
                case 'PX':
                    datastore.set_with_expiry(key, value, expiry / 1000)
                    return SimpleString('OK')
        return Error("ERR syntax error")
    return Error("ERR wrong number of arguments for 'set' command")

def _handle_get(command, datastore):
    if len(command) == 2:
        key = command[1].data.decode()
        try:
            value = datastore[key]
        except KeyError:
            return BulkString(None)
        return BulkString(value)
    return Error("ERR wrong number of arguments for 'get' command")

def _handle_unrecognised_command(command):
    args = " ".join((f"'{c.data.decode()}'" for c in command[1:]))
    return Error(
        f"ERR unknown command '{command[0].data.decode()}', with args beginning with: {args}"
    )

def handle_command(command, datastore):
    match command[0].data.decode().upper():
        case 'ECHO':
            return _handle_echo(command)
        case 'PING':
            return _handle_ping(command)
        case 'SET':
            return _handle_set(command, datastore)
        case 'GET':
            return _handle_get(command, datastore)
    return _handle_unrecognised_command(command)
