from c42secevents.extractors import INSERTION_TIMESTAMP_FIELD_NAME


class TestAEDCursorStore(object):
    def test_get_insertion_timestamp_queries_for_insertion_timestamp_where_cursor_id_is_primary_key(
        self, aed_cursor_store, execute_function
    ):
        expected_query = "SELECT {0} FROM siem_checkpoint WHERE cursor_id=?".format(
            INSERTION_TIMESTAMP_FIELD_NAME
        )
        _ = aed_cursor_store.insertion_timestamp
        execute_function.assert_called_once_with(expected_query, (aed_cursor_store._primary_key,))

    def test_set_insertion_timestamp_updates_insertion_timestamp_where_cursor_id_is_primary_key(
        self, aed_cursor_store, execute_function
    ):
        expected_query = "UPDATE siem_checkpoint SET {0}=? WHERE cursor_id = ?".format(
            INSERTION_TIMESTAMP_FIELD_NAME
        )
        new_insertion_timestamp = 123
        aed_cursor_store.insertion_timestamp = new_insertion_timestamp
        execute_function.assert_called_once_with(
            expected_query, (new_insertion_timestamp, aed_cursor_store._primary_key)
        )
