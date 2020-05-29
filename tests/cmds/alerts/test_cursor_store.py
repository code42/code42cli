from os import path

from code42cli import PRODUCT_NAME
from code42cli.cmds.search_shared.cursor_store import BaseCursorStore, AlertCursorStore


class TestBaseCursorStore(object):
    def test_init_cursor_store_when_not_given_db_file_path_uses_expected_default_checkpoints_path(
        self, sqlite_connection
    ):
        home_dir = path.expanduser("~")
        expected_path = path.join(home_dir, ".code42cli", "db")
        db_table_name = "TEST"
        expected_db_file_path = path.join(expected_path, "file_event_checkpoints.db")
        BaseCursorStore(db_table_name)
        sqlite_connection.assert_called_once_with(expected_db_file_path)

    def test_init_cursor_store_when_given_db_file_path_uses_given_path(self, sqlite_connection):
        expected_db_file_path = "Hey, look, I'm a file path..."
        BaseCursorStore("test", expected_db_file_path)
        sqlite_connection.assert_called_once_with(expected_db_file_path)


class TestAlertCursorStore(object):
    MOCK_TEST_DB_NAME = "test_path.db"

    def test_init_when_called_twice_with_different_profile_names_creates_two_rows(
        self, mocker, sqlite_connection
    ):
        mock = mocker.patch(
            "{}.cmds.search_shared.cursor_store.AlertCursorStore._row_exists".format(PRODUCT_NAME)
        )
        mock.return_value = False
        spy = mocker.spy(AlertCursorStore, "_insert_new_row")
        AlertCursorStore("Profile A", self.MOCK_TEST_DB_NAME)
        AlertCursorStore("Profile B", self.MOCK_TEST_DB_NAME)
        assert spy.call_count == 2

    def test_get_stored_cursor_timestamp_executes_expected_select_query(self, sqlite_connection):
        store = AlertCursorStore("Profile", self.MOCK_TEST_DB_NAME)
        store.get_stored_cursor_timestamp()
        with store._connection as conn:
            expected = "SELECT {0} FROM alert_checkpoints WHERE cursor_id=?".format(u"createdAt")
            actual = conn.cursor().execute.call_args[0][0]
            assert actual == expected

    def test_get_stored_cursor_timestamp_executes_query_with_expected_primary_key(
        self, sqlite_connection
    ):
        store = AlertCursorStore("Profile", self.MOCK_TEST_DB_NAME)
        store.get_stored_cursor_timestamp()
        with store._connection as conn:
            actual = conn.cursor().execute.call_args[0][1][0]
            expected = store._primary_key
            assert actual == expected

    def test_replace_stored_cursor_timestamp_executes_expected_update_query(
        self, sqlite_connection
    ):
        store = AlertCursorStore("Profile", self.MOCK_TEST_DB_NAME)
        store.replace_stored_cursor_timestamp(123)
        with store._connection as conn:
            expected = "UPDATE alert_checkpoints SET {0}=? WHERE cursor_id=?".format(u"createdAt")
            actual = conn.execute.call_args[0][0]
            assert actual == expected

    def test_replace_stored_cursor_timestamp_executes_query_with_expected_primary_key(
        self, sqlite_connection
    ):
        store = AlertCursorStore("Profile", self.MOCK_TEST_DB_NAME)
        new_cursor_timestamp = 123
        store.replace_stored_cursor_timestamp(new_cursor_timestamp)
        with store._connection as conn:
            actual = conn.execute.call_args[0][1][0]
            assert actual == new_cursor_timestamp

    def test_clean_executes_query_with_expected_primary_key(self, sqlite_connection):
        profile_name = "Profile"
        store = AlertCursorStore(profile_name, self.MOCK_TEST_DB_NAME)
        store.clean()
        with store._connection as conn:
            expected_query = "DELETE FROM {0} WHERE {1}=?".format(
                store._table_name, store._PRIMARY_KEY_COLUMN_NAME
            )
            actual_query, pk = conn.execute.call_args[0]
            assert expected_query == actual_query
            assert pk == (profile_name,)
