import errno
import logging
import os
import socket
import threading

logger = logging.getLogger(__name__)


class SocketServer:
    NUMBER_OF_CONNECTED_CLIENTS_MAX = 5

    def __init__(self, host_name='', port=50007):
        self.host_name = host_name
        self.port = port
        self._server_thread = threading.Thread(target=self._run_server)
        self._server_socket = None
        self._connected_clients = list()

    def start_server(self):
        self._create_server()
        self._server_thread.start()

    def is_server_created(self):
        return True if self._server_socket else False

    def send_data_to_connected_clients(self, data):
        if self.is_server_created():
            logger.debug(f'Send data to all connected clients')
            for client in self._connected_clients:
                try:
                    client.send(bytes(data, 'UTF-8'))
                except socket.error as e:
                    if e.errno == errno.EPIPE:
                        logger.error(f'Socket pipe error on client {client.getsockname()}: {os.strerror(e.errno)}')
                        self._disconnect_client(client)
                    else:
                        logger.error(f'Socket error on client {client.getsockname()}: {e}')

    def _create_server(self):
        logger.info(f'Create socket server on {self.host_name}:{self.port}')
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host_name, self.port))

    def _run_server(self):
        if not self.is_server_created():
            logger.warning('Could not start server thread: socket not created')
            return

        logger.info(f'Start listening to socket clients...')
        self._server_socket.listen(self.NUMBER_OF_CONNECTED_CLIENTS_MAX)

        while self.is_server_created() and True:
            client, address = self._server_socket.accept()
            logger.info(f'New client connection from {address}')
            self._connected_clients.append(client)
            self._create_client_thread(client, address)

        logger.info(f'Server thread stopped')

    def _create_client_thread(self, client, address):
        threading.Thread(target=self._run_client, args=(client, address)).start()

    def _run_client(self, client, address):
        logger.info(f'Start client {address} thread...')
        size = 1024
        while True:
            try:
                client.recv(size)
            except socket.error as e:
                if e.errno == errno.EPIPE:
                    logger.error(f'Socket pipe error on client {address}: {os.strerror(e.errno)}')
                elif e.errno == errno.EBADF:
                    logger.error(f'Bad file descriptor for client {address}')
                else:
                    logger.error(f'Socket error on client {client.getsockname()}: {e}')
                self._disconnect_client(client)
                return False

    def _disconnect_client(self, client):
        if client in self._connected_clients:
            logger.warning(f'Disconnect client {client.getsockname()} from server')
            client.close()
            self._connected_clients.remove(client)
