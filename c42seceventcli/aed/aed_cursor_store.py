from c42seceventcli.common.cursor_store import SecurityEventCursorStore

_INSERTION_TIMESTAMP_FIELD_NAME = u"insertionTimestamp"


class AEDCursorStore(SecurityEventCursorStore):
    @property
    def insertion_timestamp(self):
        rows = self._get(_INSERTION_TIMESTAMP_FIELD_NAME, self._primary_key)
        if rows:
            return rows[0]

    @insertion_timestamp.setter
    def insertion_timestamp(self, value):
        self._set(
            column_name=_INSERTION_TIMESTAMP_FIELD_NAME,
            new_value=value,
            primary_key=self._primary_key,
        )

    @property
    def _primary_key(self):
        return 1

    def _init_table(self):
        columns = "{0}, {1}".format(self._primary_key_column_name, _INSERTION_TIMESTAMP_FIELD_NAME)
        create_table_query = "CREATE TABLE {0} ({1})".format(self._table_name, columns)
        insert_query = "INSERT INTO {0} VALUES(?, null)".format(self._table_name)
        with self._connection as conn:
            conn.execute(create_table_query)
            conn.execute(insert_query, (self._primary_key,))
