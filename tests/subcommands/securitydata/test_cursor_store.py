import pytest
from os import path

from code42cli.subcommands.securitydata.cursor_store import SecurityEventCursorStore


class TestSecurityEventCursorStore(object):
    @pytest.fixture
    def sqlite_connection(self, mocker):
        return mocker.patch("sqlite3.connect")

    def test_init_cursor_store_when_not_given_db_file_path_uses_expected_path_with_db_table_name_as_db_file_name(
        self, sqlite_connection
    ):
        home_dir = path.expanduser("~")
        expected_path = path.join(home_dir, ".code42cli/db")
        expected_db_name = "TEST"
        expected_db_file_path = "{0}/{1}.db".format(expected_path, expected_db_name)
        SecurityEventCursorStore(expected_db_name)
        sqlite_connection.assert_called_once_with(expected_db_file_path)

    def test_init_cursor_store_when_given_db_file_path_uses_given_path(self, sqlite_connection):
        expected_db_file_path = "Hey, look, I'm a file path..."
        SecurityEventCursorStore("test", expected_db_file_path)
        sqlite_connection.assert_called_once_with(expected_db_file_path)
