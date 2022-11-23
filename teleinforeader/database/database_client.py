import logging

import mariadb

logger = logging.getLogger(__name__)


class DataBaseClient:

    def __init__(self, database_name: str, user: str, password: str, port=3306):
        self._database_name = database_name
        self._user = user
        self._password = password
        self._host = 'localhost'
        self._port = port
        self._connection = None

    def connect(self):
        try:
            self._connection = mariadb.connect(
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port,
                database=self._database_name
            )
            self._test_connection()
        except mariadb.Error as e:
            logger.error(f'Error connecting to MariaDB Platform: {e}')
            self._connection = None

    def insert_new_tele_info_frame(self, tele_info_frame):
        try:
            logger.debug(f'Insert new teleinfo frame into database: key={tele_info_frame.timestamp_db}')
            sql_request = self._prepare_insert_frame_request(tele_info_frame)
            cursor = self._connection.cursor()

            cursor.execute(sql_request)
            self._connection.commit()
        except mariadb.Error as e:
            logger.error(f'Error executing request to MariaDB Platform: {e}')

    def is_connected(self):
        return True if self._connection else False

    def _test_connection(self):
        cursor = self._connection.cursor()
        cursor.execute('select count(*) row_count from teleinfoframes')
        result = cursor.fetchone()

        if result:
            logger.debug(f'Successfully accessed to database: Number of frames detected: {result[0]}')
        else:
            logger.error('Failed to access to database: connection test returned nothing')

    @staticmethod
    def _prepare_insert_frame_request(tele_info_frame):
        request = 'INSERT INTO teleinfodb.teleinfoframes (' \
                  'timestamp, ' \
                  'meter_identifier, ' \
                  'subscription_type, ' \
                  'subscription_power_in_a, ' \
                  'total_base_index_in_wh, ' \
                  'current_pricing_period, ' \
                  'instantaneous_intensity_in_a, ' \
                  'intensity_max_in_a, ' \
                  'power_consumption_in_va, ' \
                  'peak_off_peak_schedule, ' \
                  'meter_state_code' \
                  ') ' \
                  'VALUES (' \
                  f"'{tele_info_frame.timestamp_db}', " \
                  f"'{tele_info_frame.meter_identifier}', " \
                  f"'{tele_info_frame.subscription_type}', " \
                  f'{tele_info_frame.subscription_power_in_a}, ' \
                  f'{tele_info_frame.total_base_index_in_wh}, ' \
                  f"'{tele_info_frame.current_pricing_period}', " \
                  f'{tele_info_frame.instantaneous_intensity_in_a}, ' \
                  f'{tele_info_frame.intensity_max_in_a}, ' \
                  f'{tele_info_frame.power_consumption_in_va}, ' \
                  f"'{tele_info_frame.peak_off_peak_schedule}', " \
                  f"'{tele_info_frame.meter_state_code}'" \
                  ')'
        return request

    def get_database_name(self) -> str:
        return self._database_name
