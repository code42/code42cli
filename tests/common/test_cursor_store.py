from c42seceventcli.common.cursor_store import SecurityEventCursorStore


class TestSecurityEventCursorStore(object):
    def test_init_cursor_store_when_not_given_db_file_path_uses_expected_path_with_db_table_name_as_db_file_name(self, mocker, sqlite_connection):
        expected_path = "TEST_PATH"
        expected_db_name = "TEST"
        mock_path = mocker.patch("os.path.dirname")
        mock_path.return_value = expected_path
        expected_db_file_path = "{0}/{1}.db".format(expected_path, expected_db_name)
        SecurityEventCursorStore(expected_db_name)
        sqlite_connection.assert_called_once_with(expected_db_file_path)

    def test_init_cursor_store_when_given_db_file_path_uses_given_path(self, mocker):
        mock_connect_function = mocker.patch("sqlite3.connect")
        expected_db_file_path = "Hey, look, I'm a file path..."
        SecurityEventCursorStore("test", expected_db_file_path)
        mock_connect_function.assert_called_once_with(expected_db_file_path)
