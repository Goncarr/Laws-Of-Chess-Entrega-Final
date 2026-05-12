import threading

class ListaCliente:
    def __init__(self):
        self.clientes = []
        self._lock = threading.Lock()

    def connect(self, connection, address):
        """
        Method that adds a cliente to the clientes list
        :param connection: Client's connection details
        :param address: Client's address
        :return:
        """
        with self._lock:
            cliente = [connection, address]
            self.clientes.append(cliente)

    def disconnect(self, address):
        """
        Method that removes a cliente from the clientes list
        :param address: Client's address
        :return:
        """
        with self._lock:
            for cliente in self.clientes:
                if cliente[1] == address:
                    self.clientes.remove(cliente)

    def count(self):
        """
        Method that returns the number of how many clients are in self.clientes
        :return: Number of clients in self.clientes
        """
        with self._lock:
            return len(self.clientes)