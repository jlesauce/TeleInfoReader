import argparse
import logging
from datetime import datetime

from teleinforeader.database.database_client import DataBaseClient
from teleinforeader.io.TeleInfoError import TeleInfoError
from teleinforeader.io.serial_client import SerialLinkClient
from teleinforeader.io.socket_server import SocketServer
from teleinforeader.model.tele_info_data import TeleInfoFrame
from teleinforeader.util.logger import configure_logger

APPLICATION_NAME = 'TeleInfo Reader'
APPLICATION_SHORT_NAME = 'teleinforeader'
SERIAL_DEVICE_FILE = '/dev/ttyAMA0'
SOCKET_SERVER_PORT = 50007
DATABASE_NAME = 'teleinfodb'
DATABASE_USER_NAME = 'jlesauce-local'
DATABASE_PASSWORD = '80PYKfEAFoLIBdB'
TELE_INFO_FRAME_DATA_STORAGE_TIME_INTERVAL_IN_S = 5

logger = logging.getLogger(__name__)

socket_server = SocketServer(port=SOCKET_SERVER_PORT)
sql_client = DataBaseClient(DATABASE_NAME, DATABASE_USER_NAME, DATABASE_PASSWORD)
last_received_frame = TeleInfoFrame()
elapsed_time_since_last_frame_in_s = 0


def main():
    args = parse_arguments()
    configure_logger(log_level=logging.getLevelName(args.log_level.upper()))

    logger.info(f'Start {APPLICATION_NAME}')

    sql_client.connect()

    if not args.no_server:
        socket_server.start_server()

    create_serial_client()


def create_serial_client():
    serial_client = SerialLinkClient(SERIAL_DEVICE_FILE)
    serial_client.subscribe_to_new_messages(on_new_tele_info_data_received)
    serial_client.start_client()


def on_new_tele_info_data_received(data: str):
    global last_received_frame, elapsed_time_since_last_frame_in_s

    try:
        tele_info_frame = create_tele_info_frame(data)
        time_diff_between_frames_in_s = compute_time_difference_in_s(last_received_frame, tele_info_frame)
        elapsed_time_since_last_frame_in_s += time_diff_between_frames_in_s
        last_received_frame = tele_info_frame

        logger.info(f'Received new TeleInfo frame {tele_info_frame.timestamp}: '
                    f'Iint(A)={tele_info_frame.instantaneous_intensity_in_a}')
        logger.debug(f'Received serial message:\n{data}')

        if socket_server.is_server_created():
            socket_server.send_data_to_connected_clients(data)

        if sql_client.is_connected() and tele_info_frame \
                and elapsed_time_since_last_frame_in_s >= TELE_INFO_FRAME_DATA_STORAGE_TIME_INTERVAL_IN_S:
            elapsed_time_since_last_frame_in_s = 0
            sql_client.insert_new_tele_info_frame(tele_info_frame)
    except TeleInfoError as e:
        logger.error(f'Invalid TeleInfo frame received: {e}')


def compute_time_difference_in_s(data_frame_0, data_frame_1):
    fmt = '%Y-%m-%d %H:%M:%S'
    timestamp_0 = datetime.strptime(data_frame_0.timestamp_db, fmt)
    timestamp_1 = datetime.strptime(data_frame_1.timestamp_db, fmt)

    if timestamp_0 > timestamp_1:
        time_difference = timestamp_0 - timestamp_1
    else:
        time_difference = timestamp_1 - timestamp_0
    return time_difference.seconds


def create_tele_info_frame(data):
    try:
        return TeleInfoFrame(data)
    except Exception as e:
        raise TeleInfoError(e, data)


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
    parser.add_argument('--log-level', dest="log_level",
                        choices=['debug', 'info', 'warn', 'error', 'fatal'], default='info',
                        help="Set the application log level")

    return parser


if __name__ == "__main__":
    main()
