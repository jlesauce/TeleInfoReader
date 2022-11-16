import argparse
import logging

from src.database.database_client import DataBaseClient
from src.io.serial_client import SerialLinkClient
from src.io.socket_server import SocketServer
from src.util.logger import configure_logger

APPLICATION_NAME = 'TeleInfo Reader'
APPLICATION_SHORT_NAME = 'teleinforeader'
SOCKET_SERVER_PORT = 50007

logger = logging.getLogger(__name__)

socket_server = SocketServer(port=SOCKET_SERVER_PORT)
sql_client = DataBaseClient()


def main():
    configure_logger(log_file=f'{APPLICATION_SHORT_NAME}.log')
    args = parse_arguments()

    logger.info(f'Start {APPLICATION_NAME}')

    sql_client.connect()

    if not args.no_server:
        socket_server.start_server()

    create_serial_client()


def create_serial_client():
    serial_client = SerialLinkClient('/dev/ttyAMA0')
    serial_client.subscribe_to_new_messages(on_new_tele_info_data_received)
    serial_client.start_client()


def on_new_tele_info_data_received(data: str):
    logger.debug(f'Received new serial message:\n{data}')

    if socket_server.is_server_created():
        socket_server.send_data_to_connected_clients(data)

    if sql_client.is_connected():
        sql_client.insert_new_tele_info_frame(data)


def parse_arguments():
    parser = create_argument_parser()
    return parser.parse_args()


def create_argument_parser():
    parser = argparse.ArgumentParser(description='Application used to read TeleInfo data frames from serial link '
                                                 'connected to Enedis Linky meter equipment. The application then '
                                                 'provides the data using a socket server on port '
                                                 + str(SOCKET_SERVER_PORT) + '. The data are also stored on a local' +
                                                 'database (' + sql_client.get_database_name() + ').')
    parser.add_argument('--no-server', action='store_true', help='Do not start the server for remote data access.')

    return parser


if __name__ == "__main__":
    main()
