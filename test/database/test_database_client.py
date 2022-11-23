import unittest
from unittest.mock import patch

import mariadb

from teleinforeader.database.database_client import DataBaseClient


class TestDataBaseClient(unittest.TestCase):

    def test_data_base_default_constructor(self):
        client = DataBaseClient(database_name='db-name', user='foo-user', password='my_password')

        assert client.get_database_name() == 'db-name'
        assert client._database_name == 'db-name'
        assert client._user == 'foo-user'
        assert client._password == 'my_password'
        assert client._host == 'localhost'
        assert client._port == 3306
        assert client._connection is None

    def test_data_base_constructor_with_custom_port(self):
        client = DataBaseClient('db-name', 'foo-user', 'my_password', port=12345)

        assert client._port == 12345

    @patch('mariadb.connect')
    def test_connect_to_mariadb(self, connect_mock):
        client = DataBaseClient('db-name', 'foo-user', 'my_password')

        client.connect()

        connect_mock.assert_called_once_with(database='db-name', user='foo-user', password='my_password',
                                             host='localhost',
                                             port=3306)

    @patch('mariadb.connect', side_effect=mariadb.Error('A mariadb error message'))
    def test_connect_to_mariadb_raise_mariadb_error(self, connect_mock):
        client = DataBaseClient('db-name', 'foo-user', 'my_password')

        with self.assertLogs(level='ERROR') as context_manager:
            client.connect()

            connect_mock.assert_called_once_with(database='db-name', user='foo-user', password='my_password',
                                                 host='localhost', port=3306)
            self.assertEqual(context_manager.output,
                             ['ERROR:teleinforeader.database.database_client:Error connecting to MariaDB '
                              'Platform: A mariadb error message'])
