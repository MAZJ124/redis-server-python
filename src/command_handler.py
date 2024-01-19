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

def _handle_exists(command, datastore):
    if len(command) > 1:
        count = 0
        for c in command[1:]:
            key = c.data.decode()
            if key in datastore:
                count += 1
        return Integer(count)
    return Error("ERR wrong number of arguments for 'exists' command")

def _handle_del(command, datastore):
    if len(command) > 1:
        count = 0
        for c in command[1:]:
            key = c.data.decode()
            if key in datastore:
                del datastore[key]
                count += 1
        return Integer(count)
    return Error("ERR wrong number of arguments for 'del' command")

def _handle_incr(command, datastore):
    if len(command) == 2:
        key = command[1].data.decode()
        try:
            return Integer(datastore.incr(key))
        except:
            return Error('ERR value is not an integer or out of range')
    return Error("ERR wrong number of arguments for 'incr' command")

def _handle_decr(command, datastore):
    if len(command) == 2:
        key = command[1].data.decode()
        try:
            return Integer(datastore.decr(key))
        except:
            return Error('ERR value is not an integer or out of range')
    return Error("ERR wrong number of arguments for 'decr' command")

def _handle_lpush(command, datastore):
    if len(command) >= 3:
        key = command[1].data.decode()
        try:
            for c in command[2:]:
                element = c.data.decode()
                count = datastore.lpush(key, element)
            return Integer(count)
        except TypeError:
            return Error('WRONGTYPE Operation against a key holding the wrong kind of value')
    return Error("ERR wrong number of arguments for 'lpush' command")

def _handle_rpush(command, datastore):
    if len(command) >= 3:
        key = command[1].data.decode()
        try:
            for c in command[2:]:
                element = c.data.decode()
                count = datastore.rpush(key, element)
            return Integer(count)
        except TypeError:
            return Error('WRONGTYPE Operation against a key holding the wrong kind of value')
    return Error("ERR wrong number of arguments for 'rpush' command")

def _handle_lrange(command, datastore):
    if len(command) == 4:
        key = command[1].data.decode()
        try:
            start, end = int(command[2].data.decode()), int(command[3].data.decode())
            result = datastore.lrange(key, start, end)
            return Array([BulkString(r) for r in result])
        except TypeError:
            return Error('WRONGTYPE Operation against a key holding the wrong kind of value LRANGE')
    return Error("ERR wrong number of arguments for 'lrange' command")

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
        case 'EXISTS':
            return _handle_exists(command, datastore)
        case 'DEL':
            return _handle_del(command, datastore)
        case 'INCR':
            return _handle_incr(command, datastore)
        case 'DECR':
            return _handle_decr(command, datastore)
        case 'LPUSH':
            return _handle_lpush(command, datastore)
        case 'RPUSH':
            return _handle_rpush(command, datastore)
        case 'LRANGE':
            return _handle_lrange(command, datastore)
    return _handle_unrecognised_command(command)
