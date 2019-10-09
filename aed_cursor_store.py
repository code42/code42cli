from os import path
import sqlite3


_INSERTION_TIMESTAMP_FIELD_NAME = u"insertionTimestamp"
_TABLE_NAME = "siem_checkpoint"
_PRIMARY_KEY_COLUMN_NAME = "cursor_id"
_PRIMARY_KEY = 1


class AEDCursorStore(object):
    def __init__(self, db_file_path=None):
        # type: (str) -> None
        if db_file_path is None:
            script_path = path.dirname(path.realpath(__file__))
            db_file_path = "{0}/{1}.db".format(script_path, _TABLE_NAME)

        self._connection = sqlite3.connect(db_file_path)
        if self._is_empty():
            self._init_table()

    @property
    def insertion_timestamp(self):
        query = "SELECT {0} FROM {1}} WHERE {2}=?".format(
            _INSERTION_TIMESTAMP_FIELD_NAME, _TABLE_NAME, _PRIMARY_KEY_COLUMN_NAME
        )
        with self._connection as conn:
            cursor = conn.cursor()
            cursor.execute(query, (_PRIMARY_KEY,))
            rows = cursor.fetchone()
            if rows:
                return rows[0]

    @insertion_timestamp.setter
    def insertion_timestamp(self, value):
        query = "UPDATE {0}} SET {1}=? WHERE {2}=?".format(
            _TABLE_NAME,
            _INSERTION_TIMESTAMP_FIELD_NAME,
            _PRIMARY_KEY_COLUMN_NAME
        )
        with self._connection as conn:
            conn.execute(query, (value, _PRIMARY_KEY,))

    def reset(self):
        self._drop_table()
        self._init_table()

    def _init_table(self):
        columns = "{0}, {1}".format(_PRIMARY_KEY_COLUMN_NAME, _INSERTION_TIMESTAMP_FIELD_NAME)
        create_table_query = "CREATE TABLE {0} ({1})".format(_TABLE_NAME, columns)
        insert_query = "INSERT INTO {0} VALUES(?, null)".format(_TABLE_NAME)
        with self._connection as conn:
            conn.execute(create_table_query)
            conn.execute(insert_query, (_PRIMARY_KEY,))

    def _drop_table(self):
        drop_query = "DROP TABLE {0}".format(_TABLE_NAME)
        with self._connection as conn:
            conn.execute(drop_query)

    def _is_empty(self):
        table_count_query = """
            SELECT COUNT(name)
            FROM sqlite_master
            WHERE type='table' AND name=?
        """
        with self._connection as conn:
            cursor = conn.cursor()
            cursor.execute(table_count_query, (_TABLE_NAME,))
            query_result = cursor.fetchone()
            if query_result:
                return int(query_result[0]) <= 0
