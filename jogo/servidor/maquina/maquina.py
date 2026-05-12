import json
import servidor
from servidor.client_list.lista_clientes import ListaCliente
from servidor.matches.matchManager import MatchManager
from servidor.processing_files.processa_cliente import ProcessaCliente
from servidor.processing_files.processa_gestor import ProcessaGestor
import socket


class Maquina:
    def __init__(self):
        self.clientes = ListaCliente()
        self.s = socket.socket()
        self.s.bind(('', servidor.PORT))
        self.matchManager = MatchManager()

    # ---------------------- interaction with sockets ------------------------------

    def receive_int(self, connection, n_bytes: int) -> int:
        """
        :param n_bytes: The number of bytes to read from the current connection
        :return: The next integer read from the current connection
        """
        data = b""
        while len(data) < n_bytes:
            chunk = connection.recv(n_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_int(self, connection, value: int, n_bytes: int) -> None:
        """
        :param value: The integer value to be sent to the current connection
        :param n_bytes: The number of bytes to send
        """
        connection.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_str(self, connection, n_bytes: int) -> str:
        """
        :param n_bytes: The number of bytes to read from the current connection
        :return: The next string read from the current connection
        """
        data = b""
        while len(data) < n_bytes:
            chunk = connection.recv(n_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return data.decode()

    def send_str(self, connection, value: str) -> None:
        """
        :param value: The string value to send to the current connection
        """
        connection.send(value.encode())  # Fixed: was connection.connection.send(...)

    def send_object(self, connection, obj) -> None:
        """1º: envia tamanho, 2º: envia dados."""
        data = json.dumps(obj).encode('utf-8')
        size = len(data)
        self.send_int(connection, size, servidor.INT_SIZE)  # Envio do tamanho
        connection.send(data)                               # Envio do objeto

    def receive_object(self, connection):
        """1º: lê tamanho, 2º: lê dados."""
        size = self.receive_int(connection, servidor.INT_SIZE)  # Recebe o tamanho
        data = b""
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return json.loads(data.decode('utf-8'))

    # ---------------------- server loop ------------------------------

    def execute(self):
        """
        This method starts the server and checks whether the person joining the
        server is a client or gestor
        """
        self.s.listen(50)
        print("Waiting for clients on port " + str(servidor.PORT))
        while True:
            print("On accept...")
            try:
                connection, address = self.s.accept()
            except OSError as e:
                print(f"Server socket error: {e}")
                break

            # This allows to check which players are active in the server
            print("Client", address, "connected")

            identify = self.receive_str(connection, servidor.COMMAND_SIZE)

            if identify == servidor.GESTOR_ID:
                print(f"{address} identified as GESTOR")
                processo = ProcessaGestor(connection, address, self.clientes, self.matchManager)

            else:
                print(f"{address} identified as CLIENTE")
                self.clientes.connect(connection, address)
                processo = ProcessaCliente(connection, address, self.clientes, self.matchManager)

            processo.start()


