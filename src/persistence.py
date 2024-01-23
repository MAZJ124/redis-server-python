from src.command_handler import handle_command
from src.protocol_handler import extract_frame_from_buffer
from src.types import Error


class AppendOnlyPersister:
    def __init__(self, filename):
        self._filename = filename
        self._file = open(filename, mode="ab", buffering=0)

    def log_command(self, command):
        self._file.write(f"*{len(command)}\r\n".encode())
        for item in command:
            self._file.write(item.file_encode())

def restore_db(filename, datastore):
    buffer = bytearray()
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                buffer.extend(data)
                while True:
                    frame, frame_size = extract_frame_from_buffer(buffer)
                    if frame:
                        buffer = buffer[frame_size:]
                        result = handle_command(frame, datastore)
                        if isinstance(result, Error):
                            print('Error corrupt AOF file')
                            return False
                    else:
                        break
    except FileNotFoundError:
        with open(filename, 'w'):
            return True
    return True
