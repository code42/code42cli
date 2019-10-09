from c42seceventcli.common.cursor_store import SecurityEventCursorStore


class TestSecurityEventCursorStore(object):
    def test_reset_calls_connection_drop_table_query(self, test_store, execute_function):
        test_store.reset()
        execute_function.assert_called_once_with("DROP TABLE siem_checkpoint")

    def test_init_cursor_store_when_not_given_db_file_path_used_expected_path(self, mocker):
        expected_path = "TEST_PATH"
        mock_connect_function = mocker.patch("sqlite3.connect")
        mock_path = mocker.patch("os.path.dirname")
        mock_path.return_value = expected_path
        expected_db_file_path = "{0}/siem_checkpoint.db".format(expected_path)
        SecurityEventCursorStore()
        mock_connect_function.assert_called_once_with(expected_db_file_path)

    def test_init_cursor_store_when_given_db_file_path_uses_given_path(self, mocker):
        mock_connect_function = mocker.patch("sqlite3.connect")
        expected_db_file_path = "Hey, look, I'm a file path..."
        SecurityEventCursorStore(expected_db_file_path)
        mock_connect_function.assert_called_once_with(expected_db_file_path)
