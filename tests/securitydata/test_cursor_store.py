from os import path
import pytest

from c42eventextractor.extractors import INSERTION_TIMESTAMP_FIELD_NAME
from code42cli.securitydata.cursor_store import BaseCursorStore, FileEventCursorStore


@pytest.fixture
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")


class TestBaseCursorStore(object):
    def test_init_cursor_store_when_not_given_db_file_path_uses_expected_path_with_db_table_name_as_db_file_name(
        self, sqlite_connection
    ):
        home_dir = path.expanduser("~")
        expected_path = path.join(home_dir, ".code42cli/db")
        expected_db_name = "TEST"
        expected_db_file_path = "{0}/{1}.db".format(expected_path, expected_db_name)
        BaseCursorStore(expected_db_name)
        sqlite_connection.assert_called_once_with(expected_db_file_path)

    def test_init_cursor_store_when_given_db_file_path_uses_given_path(self, sqlite_connection):
        expected_db_file_path = "Hey, look, I'm a file path..."
        BaseCursorStore("test", expected_db_file_path)
        sqlite_connection.assert_called_once_with(expected_db_file_path)


class TestFileEventCursorStore(object):
    MOCK_TEST_DB_PATH = "test_path.db"

    def test_reset_executes_expected_drop_table_query(self, sqlite_connection):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args_list[0][0][0]
            expected = "DROP TABLE file_event_checkpoints"
            assert actual == expected

    def test_reset_executes_expected_create_table_query(self, sqlite_connection):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args_list[1][0][0]
            expected = "CREATE TABLE file_event_checkpoints (cursor_id, insertionTimestamp)"
            assert actual == expected

    def test_reset_executes_expected_insert_query(self, sqlite_connection):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store._connection = sqlite_connection
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args[0][0]
            expected = "INSERT INTO file_event_checkpoints VALUES(?, null)"
            assert actual == expected

    def test_reset_executes_query_with_expected_primary_key(self, sqlite_connection):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store._connection = sqlite_connection
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args[0][1][0]
            expected = store._primary_key
            assert actual == expected

    def test_get_stored_insertion_timestamp_executes_expected_select_query(self, sqlite_connection):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store.get_stored_insertion_timestamp()
        with store._connection as conn:
            expected = "SELECT {0} FROM file_event_checkpoints WHERE cursor_id=?".format(
                INSERTION_TIMESTAMP_FIELD_NAME
            )
            actual = conn.cursor().execute.call_args[0][0]
            assert actual == expected

    def test_get_stored_insertion_timestamp_executes_query_with_expected_primary_key(
        self, sqlite_connection
    ):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store.get_stored_insertion_timestamp()
        with store._connection as conn:
            actual = conn.cursor().execute.call_args[0][1][0]
            expected = store._primary_key
            assert actual == expected

    def test_replace_stored_insertion_timestamp_executes_expected_update_query(
        self, sqlite_connection
    ):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        store.replace_stored_insertion_timestamp(123)
        with store._connection as conn:
            expected = "UPDATE file_event_checkpoints SET {0}=? WHERE cursor_id=?".format(
                INSERTION_TIMESTAMP_FIELD_NAME
            )
            actual = conn.execute.call_args[0][0]
            assert actual == expected

    def test_replace_stored_insertion_timestamp_executes_query_with_expected_primary_key(
        self, sqlite_connection
    ):
        store = FileEventCursorStore(self.MOCK_TEST_DB_PATH)
        new_insertion_timestamp = 123
        store.replace_stored_insertion_timestamp(new_insertion_timestamp)
        with store._connection as conn:
            actual = conn.execute.call_args[0][1][0]
            assert actual == new_insertion_timestamp
