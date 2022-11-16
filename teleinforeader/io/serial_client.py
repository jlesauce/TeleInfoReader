import json
import logging
import threading

import serial
from observable import Observable

from teleinforeader.util.tele_info_helpers import is_valid_tele_info, extract_value_from_entry, get_current_timestamp, flatten_json

logger = logging.getLogger(__name__)


class SerialLinkClient:
    OBSERVABLE_NEW_MASSAGE_EVENT = 'new_message'

    def __init__(self, serial_link_file):
        self._serial_link_file = serial_link_file
        self._serial_port = None
        self._serial_thread = threading.Thread(target=self._run_client)
        self.observable = Observable()

    def subscribe_to_new_messages(self, function):
        self.observable.on(self.OBSERVABLE_NEW_MASSAGE_EVENT, function)

    def start_client(self):
        self._serial_port = self._create_serial_port()
        self._serial_thread.start()

    def is_serial_port_created(self):
        return True if self._serial_port else False

    def _create_serial_port(self):
        logger.info(f'Open serial link {self._serial_link_file}')
        return serial.Serial(self._serial_link_file, baudrate=1200, bytesize=7, timeout=1,
                             stopbits=serial.STOPBITS_ONE)

    def _run_client(self):
        if not self.is_serial_port_created():
            logger.warning('Could not start serial client thread: serial port not created')
            return

        logger.info(f'Start TeleInfo reading...')

        frame = list()
        first_frame_detected = False

        while self.is_serial_port_created() and True:
            entry = self._read_tele_info_entry()

            if is_valid_tele_info(entry):
                if self._is_start_of_frame(entry):
                    first_frame_detected = True
                    if len(frame):
                        self._collect_frame(frame)
                        frame.clear()

                if first_frame_detected:
                    frame.append(entry)

        logger.info(f'Serial client thread stopped')

    def _collect_frame(self, frame):
        frame_dict = {}
        for entry in frame:
            key, value = extract_value_from_entry(entry)
            frame_dict[key] = value

        json_entry_element = {
            'timestamp': get_current_timestamp(),
            'frame': frame_dict
        }
        json_object = json.dumps(json_entry_element, indent=4)
        logger.debug(f'Received TeleInfo frame: {flatten_json(json_object)}')

        self._notify_new_message_incoming_to_subscribers(json_object)

    def _notify_new_message_incoming_to_subscribers(self, message):
        if self.is_serial_port_created():
            logger.debug(f'Notify {self.OBSERVABLE_NEW_MASSAGE_EVENT} event received')
            self.observable.trigger(self.OBSERVABLE_NEW_MASSAGE_EVENT, message)

    def _read_tele_info_entry(self):
        # Read data out of the buffer until a carriage return / new line is found
        return self._serial_port.readline().decode('Ascii').strip()

    @staticmethod
    def _is_start_of_frame(entry):
        return entry.startswith('ADCO ')
