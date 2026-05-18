import json
import queue
import servidor
from servidor.matches.match import Match
import socket
import threading
import select


class MatchManager:
    def __init__(self):
        self.waiting_queue = queue.Queue()  # Players waiting for a game
        self.active_matches = []  # List of Match objects
        self._lock = threading.Lock()

    # ---------------------- interaction with sockets ------------------------------

    def receive_int(self, connect: socket.socket, n_bytes: int) -> int:
        data = b""
        while len(data) < n_bytes:
            chunk = connect.recv(n_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_int(self, connect: socket.socket, value: int, n_bytes: int) -> None:
        connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_str(self, connect, n_bytes: int) -> str:
        data = b""
        while len(data) < n_bytes:
            chunk = connect.recv(n_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return data.decode()

    def send_str(self, connect, value: str) -> None:
        connect.send(value.encode())

    def send_object(self, connection, obj) -> None:
        """1º: envia tamanho, 2º: envia dados."""
        data = json.dumps(obj).encode('utf-8')
        size = len(data)
        self.send_int(connection, size, servidor.INT_SIZE)
        connection.send(data)

    def receive_object(self, connection):
        """1º: lê tamanho, 2º: lê dados."""
        size = self.receive_int(connection, servidor.INT_SIZE)
        data = b""
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return json.loads(data.decode('utf-8'))

    # ---------------------- match management ------------------------------

    def add_player(self, player_socket, player_name):
        while not self.waiting_queue.empty():
            # Unpack the tuple from the queue
            opponent_socket, opponent_name = self.waiting_queue.get()

            try:
                r, _, _ = select.select([opponent_socket], [], [], 0.0)
                if r:
                    data = opponent_socket.recv(1, socket.MSG_PEEK)
                    if not data:
                        print("[MatchManager] Ghost socket detected and removed.")
                        opponent_socket.close()
                        continue
            except OSError:
                print("[MatchManager] Ghost socket detected (Error) and removed.")
                opponent_socket.close()
                continue

            # Pass BOTH names into the Match constructor
            new_match = Match(self.active_matches, opponent_socket, opponent_name, player_socket, player_name)
            with self._lock:
                self.active_matches.append(new_match)
            match_thread = threading.Thread(target=new_match.start_game, daemon=True)
            match_thread.start()
            return new_match

        # Put BOTH into the queue as a tuple
        self.waiting_queue.put((player_socket, player_name))
        return None