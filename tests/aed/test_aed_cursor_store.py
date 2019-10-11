from c42secevents.extractors import INSERTION_TIMESTAMP_FIELD_NAME
from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from ..conftest import MOCK_TEST_DB_PATH


class TestAEDCursorStore(object):
    def test_reset_calls_drop_table_query_first(self, mocker, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        execute_function = mocker.MagicMock()
        store._connection = sqlite_connection
        with store._connection as conn:
            mock_cursor = mocker.MagicMock()
            mock_cursor.execute = execute_function
            conn.cursor.return_value = mock_cursor
            conn.execute = execute_function
        store.reset()
        actual = execute_function.call_args_list[0][0][0]
        expected = "DROP TABLE siem_checkpoint"
        assert actual == expected

    def test_reset_calls_create_table_query_second(self, mocker, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        execute_function = mocker.MagicMock()
        store._connection = sqlite_connection
        with store._connection as conn:
            mock_cursor = mocker.MagicMock()
            mock_cursor.execute = execute_function
            conn.cursor.return_value = mock_cursor
            conn.execute = execute_function

        store.reset()
        actual = execute_function.call_args_list[1][0][0]
        expected = "CREATE TABLE siem_checkpoint (cursor_id, insertionTimestamp)"
        assert actual == expected

    def test_reset_calls_insert_query_third(self, mocker, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        execute_function = mocker.MagicMock()
        store._connection = sqlite_connection
        with store._connection as conn:
            mock_cursor = mocker.MagicMock()
            mock_cursor.execute = execute_function
            conn.cursor.return_value = mock_cursor
            conn.execute = execute_function
        store.reset()
        actual = execute_function.call_args_list[2][0][0]
        expected = "INSERT INTO siem_checkpoint VALUES(?, null)"
        assert actual == expected

    def test_get_insertion_timestamp_queries_for_insertion_timestamp_where_cursor_id_is_primary_key(
        self, mocker, sqlite_connection
    ):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        execute_function = mocker.MagicMock()
        store._connection = sqlite_connection
        with store._connection as conn:
            mock_cursor = mocker.MagicMock()
            mock_cursor.execute = execute_function
            conn.cursor.return_value = mock_cursor
            conn.execute = execute_function
        expected_query = "SELECT {0} FROM siem_checkpoint WHERE cursor_id=?".format(
            INSERTION_TIMESTAMP_FIELD_NAME
        )
        store.get_stored_insertion_timestamp()
        execute_function.assert_called_once_with(expected_query, (store._PRIMARY_KEY,))

    def test_set_insertion_timestamp_updates_insertion_timestamp_where_cursor_id_is_primary_key(
        self, mocker, sqlite_connection
    ):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        execute_function = mocker.MagicMock()
        store._connection = sqlite_connection
        with store._connection as conn:
            mock_cursor = mocker.MagicMock()
            mock_cursor.execute = execute_function
            conn.cursor.return_value = mock_cursor
            conn.execute = execute_function
        expected_query = "UPDATE siem_checkpoint SET {0}=? WHERE cursor_id = ?".format(
            INSERTION_TIMESTAMP_FIELD_NAME
        )
        new_insertion_timestamp = 123
        store.replace_stored_insertion_timestamp(new_insertion_timestamp)
        execute_function.assert_called_once_with(
            expected_query, (new_insertion_timestamp, store._PRIMARY_KEY)
        )
