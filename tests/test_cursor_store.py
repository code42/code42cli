from os import path

import pytest
from c42sec.cursor_store import SecurityEventCursorStore

MOCK_TEST_DB_PATH = "test_path.db"


@pytest.fixture
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")


class TestSecurityEventCursorStore(object):
    def test_init_cursor_store_when_not_given_db_file_path_uses_expected_path_with_db_table_name_as_db_file_name(
        self, sqlite_connection
    ):
        home_dir = path.expanduser("~")
        expected_path = path.join(home_dir, ".c42sec/db")
        expected_db_name = "TEST"
        expected_db_file_path = "{0}/{1}.db".format(expected_path, expected_db_name)
        SecurityEventCursorStore(expected_db_name)
        sqlite_connection.assert_called_once_with(expected_db_file_path)

    def test_init_cursor_store_when_given_db_file_path_uses_given_path(self, mocker):
        mock_connect_function = mocker.patch("sqlite3.connect")
        expected_db_file_path = "Hey, look, I'm a file path..."
        SecurityEventCursorStore("test", expected_db_file_path)
        mock_connect_function.assert_called_once_with(expected_db_file_path)
