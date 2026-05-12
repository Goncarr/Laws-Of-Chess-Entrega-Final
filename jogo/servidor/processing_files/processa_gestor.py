import gestor
import json
from servidor.client_list.lista_clientes import ListaCliente
import socket
import threading


class ProcessaGestor(threading.Thread):
    def __init__(self, connection, address, clientes: ListaCliente, matchManager):
        super().__init__()
        self.connection = connection
        self.address = address
        self.matchManager = matchManager
        self.clientes = clientes

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
        self.send_int(connection, size, gestor.INT_SIZE)
        connection.send(data)

    def receive_object(self, connection):
        """1º: lê tamanho, 2º: lê dados."""
        size = self.receive_int(connection, gestor.INT_SIZE)
        data = b""
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return json.loads(data.decode('utf-8'))




    def run(self):
        """
        This method handles the requests of "online" and "games".
        "online" -> Checks the amount of players in the server
        "games" -> Checks the amount of active matches
        """
        print(f"Gestor {self.address} conectado")
        try:
            while True:
                request_type = self.receive_str(self.connection, gestor.COMMAND_SIZE)

                if request_type == gestor.STATS_ONLINE:
                    count = self.clientes.count()
                    self.send_int(self.connection, count, gestor.INT_SIZE)

                elif request_type == gestor.STATS_GAMES:
                    count = len(self.matchManager.active_matches)
                    self.send_int(self.connection, count, gestor.INT_SIZE)

                elif request_type == gestor.END_OP:
                    break

                else:
                    print(f"Gestor {self.address} sent unrecognised command: {request_type!r}")

        except (ConnectionResetError, ConnectionError, OSError) as e:
            print(f"Gestor {self.address} desconectou inesperadamente: {e}")
        finally:
            print(f"Gestor {self.address} desconectou")
            self.connection.close()