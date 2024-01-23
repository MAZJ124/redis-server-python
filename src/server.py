import socket
import threading
from src.command_handler import handle_command
from src.datastore import DataStore

from src.protocol_handler import encode_message, extract_frame_from_buffer 

RECV_SIZE = 1024

def handle_client_connection(client_socket, datastore, persister):
    buffer = bytearray()
    try:
        while True:
            data = client_socket.recv(RECV_SIZE)
            if not data:
                break
            buffer.extend(data)
            frame, frame_size = extract_frame_from_buffer(data)
            if frame:
                buffer = buffer[frame_size:]
                result = handle_command(frame, datastore, persister)
                print(result) # for dev testing purpose only
                client_socket.send(encode_message(result))
    finally:
        client_socket.close()

class Server:
    def __init__(self, port, datastore, persister):
        self.port = port
        self._running = False
        self._datastore = datastore
        self._persister = persister

    def run(self):
        self._running = True

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            self._server_socket = server_socket
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_address = ("localhost", self.port)
            server_socket.bind(server_address)
            server_socket.listen()
            while self._running:
                comm_socket, _ = server_socket.accept()
                client_thread = threading.Thread(
                    target=handle_client_connection, args=(comm_socket, self._datastore, self._persister)
                )
                client_thread.start()

    def stop(self):
        self._running = False
