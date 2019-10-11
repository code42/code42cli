from c42seceventcli.common.cursor_store import SecurityEventCursorStore

_INSERTION_TIMESTAMP_FIELD_NAME = u"insertionTimestamp"


class AEDCursorStore(SecurityEventCursorStore):
    _PRIMARY_KEY = 1

    def __init__(self, db_file_path=None):
        super().__init__(db_file_path)
        if self._is_empty():
            self._init_table()

    def get_stored_insertion_timestamp(self):
        rows = self._get(_INSERTION_TIMESTAMP_FIELD_NAME, self._PRIMARY_KEY)
        if rows and rows[0]:
            return rows[0][0]

    def replace_stored_insertion_timestamp(self, new_insertion_timestamp):
        self._set(
            column_name=_INSERTION_TIMESTAMP_FIELD_NAME,
            new_value=new_insertion_timestamp,
            primary_key=self._PRIMARY_KEY,
        )

    def reset(self):
        self._drop_table()
        self._init_table()

    def _init_table(self):
        columns = "{0}, {1}".format(self._PRIMARY_KEY_COLUMN_NAME, _INSERTION_TIMESTAMP_FIELD_NAME)
        create_table_query = "CREATE TABLE {0} ({1})".format(self._TABLE_NAME, columns)
        insert_query = "INSERT INTO {0} VALUES(?, null)".format(self._TABLE_NAME)
        with self._connection as conn:
            conn.execute(create_table_query)
            conn.execute(insert_query, (self._PRIMARY_KEY,))
