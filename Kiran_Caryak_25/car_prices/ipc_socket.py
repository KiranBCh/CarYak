from datetime import datetime
from contextlib import AbstractContextManager
import random
import string
from random import randrange
import socket
import os


class Connection(AbstractContextManager):
    def __init__(self, custom_socket: socket.socket) -> None:
        self.socket = custom_socket
        self.recv_buffer_size = 2**20

    def send(self, message: str, timeout: float):
        self.socket.settimeout(timeout)
        self.socket.sendall(message.encode() + b'\0')

    def recv(self, timeout: float):
        data = b''

        start_time = datetime.utcnow()
        current_time = start_time
        while(len(data) == 0 or data[-1] != 0):
            time_left = timeout - (current_time - start_time).total_seconds()
            if time_left > 0:
                self.socket.settimeout(time_left)
                data = data + self.socket.recv(self.recv_buffer_size)

            else:
                raise TimeoutError

        return data[:-1].decode()

    def close(self) -> None:
        self.socket.close()

    def __exit__(self, type, value, traceback) -> bool:
        self.close()
        return False


class Client(Connection):
    def __init__(self) -> None:
        super().__init__(socket.socket(socket.AF_UNIX))

    def connect(self, address: str, timeout: float) -> None:
        self.socket.settimeout(timeout)
        self.socket.connect(address)


class Server(AbstractContextManager):
    def __init__(self, socket_dir: str, max_connections: int = 1) -> None:
        self.socket = socket.socket(socket.AF_UNIX)
        while True:
            try:
                self.address = f'{socket_dir}/{"".join(random.choices(string.digits, k=32))}.sock' 
                self.socket.bind(self.address)
                break
            except OSError:
                pass

        self.socket.listen(max_connections)

    def accept(self, timeout: float):
        self.socket.settimeout(timeout)
        conn, _ = self.socket.accept()
        return Connection(conn)

    def close(self) -> None:
        os.remove(self.address)
        self.socket.close()

    def __exit__(self, type, value, traceback) -> bool:
        self.close()
        return False
