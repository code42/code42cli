from c42secevents.extractors import INSERTION_TIMESTAMP_FIELD_NAME
from c42seceventcli.aed.cursor_store import AEDCursorStore
from tests.conftest import MOCK_TEST_DB_PATH


class TestAEDCursorStore(object):
    def test_reset_executes_expected_drop_table_query(self, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args_list[0][0][0]
            expected = "DROP TABLE siem_checkpoint"
            assert actual == expected

    def test_reset_executes_expected_create_table_query(self, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args_list[1][0][0]
            expected = "CREATE TABLE siem_checkpoint (cursor_id, insertionTimestamp)"
            assert actual == expected

    def test_reset_executes_expected_insert_query(self, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        store._connection = sqlite_connection
        store.reset()
        with store._connection as conn:
            actual = conn.execute.call_args[0][0]
            expected = "INSERT INTO siem_checkpoint VALUES(?, null)"
            assert actual == expected

    def test_get_stored_insertion_timestamp_executes_expected_select_query(self, sqlite_connection):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        store.get_stored_insertion_timestamp()
        with store._connection as conn:
            expected = "SELECT {0} FROM siem_checkpoint WHERE cursor_id=?".format(
                INSERTION_TIMESTAMP_FIELD_NAME
            )
            actual = conn.cursor().execute.call_args[0][0]
            assert actual == expected

    def test_replace_stored_insertion_timestamp_executes_expected_update_query(
        self, sqlite_connection
    ):
        store = AEDCursorStore(MOCK_TEST_DB_PATH)
        new_insertion_timestamp = 123
        store.replace_stored_insertion_timestamp(new_insertion_timestamp)
        with store._connection as conn:
            expected = "UPDATE siem_checkpoint SET {0}=? WHERE cursor_id = ?".format(
                INSERTION_TIMESTAMP_FIELD_NAME, new_insertion_timestamp
            )
            actual = conn.execute.call_args[0][0]
            assert actual == expected
