import json
import socket
import gestor


class Gestor:
    def __init__(self):
        self.connection = socket.socket()
        self.connection.connect((gestor.SERVER_ADDRESS, gestor.PORT))

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

    def execute(self):
        """
        This method allows the Gestor to get the amount of players online in the server
        and the amount of matches that are happening at the moment.

        "online" -> Checks the amount of players in the server
        "games" -> Checks the amount of active matches
        """
        self.send_str(self.connection, gestor.GESTOR_ID)

        res = ""
        while res != ".":
            res = input("Command (online / games / '.' to quit): ").strip().lower()

            if res == "online":
                self.send_str(self.connection, gestor.STATS_ONLINE)
                count = self.receive_int(self.connection, gestor.INT_SIZE)
                print(f"Jogadores online: {count}")

            elif res == "games":
                self.send_str(self.connection, gestor.STATS_GAMES)
                count = self.receive_int(self.connection, gestor.INT_SIZE)
                print(f"Jogos em curso: {count}")

        self.send_str(self.connection, gestor.END_OP)
        self.connection.close()