import sqlite3
from os import path


class SecurityEventCursorStore(object):
    _TABLE_NAME = "siem_checkpoint"
    _PRIMARY_KEY_COLUMN_NAME = "cursor_id"

    def __init__(self, db_file_path=None):
        # type: (str) -> None
        if db_file_path is None:
            script_path = path.dirname(path.realpath(__file__))
            db_file_path = "{0}/{1}.db".format(script_path, self._TABLE_NAME)

        self._connection = sqlite3.connect(db_file_path)
        if self._is_empty():
            self._init_table()

    def reset(self):
        self._drop_table()
        self._init_table()

    def _get(self, columns, primary_key):
        # type: (str, any) -> list
        query = "SELECT {0} FROM {1} WHERE {2}=?"
        query = query.format(columns, self._TABLE_NAME, self._PRIMARY_KEY_COLUMN_NAME)
        with self._connection as conn:
            cursor = conn.cursor()
            cursor.execute(query, (primary_key,))
            return cursor.fetchall()

    def _set(self, column_name, new_value, primary_key):
        # type: (str, any, any) -> None
        query = "UPDATE {0} SET {1}=? WHERE {2} = ?".format(
            self._TABLE_NAME, column_name, self._PRIMARY_KEY_COLUMN_NAME
        )
        with self._connection as conn:
            conn.execute(query, (new_value, primary_key))

    def _drop_table(self):
        drop_query = "DROP TABLE {0}".format(self._TABLE_NAME)
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
            cursor.execute(table_count_query, (self._TABLE_NAME,))
            query_result = cursor.fetchone()
            if query_result:
                return int(query_result[0]) <= 0
