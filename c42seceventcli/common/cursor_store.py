import sqlite3

from c42seceventcli.common.common import get_project_path


class SecurityEventCursorStore(object):
    _PRIMARY_KEY_COLUMN_NAME = "cursor_id"

    def __init__(self, db_table_name, db_file_path=None):
        # type: (str, str) -> None
        self._table_name = db_table_name
        if db_file_path is None:
            save_path = get_project_path()
            db_file_path = "{0}/{1}.db".format(save_path, self._table_name)

        self._connection = sqlite3.connect(db_file_path)

    def _get(self, columns, primary_key):
        # type: (str, any) -> list
        query = "SELECT {0} FROM {1} WHERE {2}=?"
        query = query.format(columns, self._table_name, self._PRIMARY_KEY_COLUMN_NAME)
        with self._connection as conn:
            cursor = conn.cursor()
            cursor.execute(query, (primary_key,))
            return cursor.fetchall()

    def _set(self, column_name, new_value, primary_key):
        # type: (str, any, any) -> None
        query = "UPDATE {0} SET {1}=? WHERE {2} = ?".format(
            self._table_name, column_name, self._PRIMARY_KEY_COLUMN_NAME
        )
        with self._connection as conn:
            conn.execute(query, (new_value, primary_key))

    def _drop_table(self):
        drop_query = "DROP TABLE {0}".format(self._table_name)
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
            cursor.execute(table_count_query, (self._table_name,))
            query_result = cursor.fetchone()
            if query_result:
                return int(query_result[0]) <= 0
