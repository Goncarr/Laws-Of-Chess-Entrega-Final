import json
import servidor
from servidor.client_list.lista_clientes import ListaCliente
from servidor.accounts.account import Account
import socket
import threading

class ProcessaCliente(threading.Thread):
    def __init__(self, connection, address, clientes: ListaCliente, matchManager):
        super().__init__()
        self.connection = connection
        self.address = address
        self.matchManager = matchManager
        self.clientes = clientes
        self.accounts = Account()
        self.account: Account = None
        self.player_name = "Guest"

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

    # ---------------------- thread loop ------------------------------

    def run(self):
        """
        This method allows to process the requests of "play", "login" and ".".
        "play" -> Sends the client to matchmaking
        "login" -> Checks if the account exists
        "." -> Disconnects the client
        """
        print(self.address, "Thread iniciada")
        handed_off = False
        try:
            while True:
                request_type = self.receive_str(self.connection, servidor.COMMAND_SIZE)

                if request_type == servidor.PLAY:
                    self.send_object(self.connection, "PLEASE WAIT")
                    # Pass BOTH the connection and the name to the queue
                    self.matchManager.add_player(self.connection, self.player_name)
                    handed_off = True
                    return

                elif request_type == servidor.LOGIN:
                    name = self.receive_object(self.connection)
                    account = self.accounts.get_account(name)
                    if account:
                        status = "Valid Login!"
                        self.player_name = name  # <--- SAVE THE NAME HERE
                    else:
                        status = "Invalid Login!"
                    self.send_object(self.connection, status)

                elif request_type == servidor.END_OP:
                    break

                else:
                    print(f"{self.address} sent unrecognised command: {request_type!r}")

        except (ConnectionResetError, ConnectionError, OSError) as e:
            print(f"{self.address} disconnected unexpectedly: {e}")
        finally:
            print("Client", self.address, "disconnected")
            self.clientes.disconnect(self.address)
            if not handed_off:
                self.connection.close()