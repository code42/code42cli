from __future__ import with_statement
import sqlite3

from code42cli.util import get_user_project_path

_INSERTION_TIMESTAMP_FIELD_NAME = u"insertionTimestamp"


class SecurityEventCursorStore(object):
    _PRIMARY_KEY_COLUMN_NAME = u"cursor_id"

    def __init__(self, db_table_name, db_file_path=None):
        self._table_name = db_table_name
        if db_file_path is None:
            db_path = get_user_project_path(u"db")
            db_file_path = u"{0}/{1}.db".format(db_path, self._table_name)

        self._connection = sqlite3.connect(db_file_path)

    def _get(self, columns, primary_key):
        query = u"SELECT {0} FROM {1} WHERE {2}=?"
        query = query.format(columns, self._table_name, self._PRIMARY_KEY_COLUMN_NAME)
        with self._connection as conn:
            cursor = conn.cursor()
            cursor.execute(query, (primary_key,))
            return cursor.fetchall()

    def _set(self, column_name, new_value, primary_key):
        query = u"UPDATE {0} SET {1}=? WHERE {2}=?".format(
            self._table_name, column_name, self._PRIMARY_KEY_COLUMN_NAME
        )
        with self._connection as conn:
            conn.execute(query, (new_value, primary_key))

    def _drop_table(self):
        drop_query = u"DROP TABLE {0}".format(self._table_name)
        with self._connection as conn:
            conn.execute(drop_query)

    def _is_empty(self):
        table_count_query = u"""
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


class AEDCursorStore(SecurityEventCursorStore):
    _PRIMARY_KEY = 1

    def __init__(self, db_file_path=None):
        super(AEDCursorStore, self).__init__(u"aed_checkpoint", db_file_path)
        if self._is_empty():
            self._init_table()

    def get_stored_insertion_timestamp(self):
        """Gets the last stored insertion timestamp."""
        rows = self._get(_INSERTION_TIMESTAMP_FIELD_NAME, self._PRIMARY_KEY)
        if rows and rows[0]:
            return rows[0][0]

    def replace_stored_insertion_timestamp(self, new_insertion_timestamp):
        """Replaces the last stored insertion timestamp with the given one."""
        self._set(
            column_name=_INSERTION_TIMESTAMP_FIELD_NAME,
            new_value=new_insertion_timestamp,
            primary_key=self._PRIMARY_KEY,
        )

    def reset(self):
        self._drop_table()
        self._init_table()

    def _init_table(self):
        columns = u"{0}, {1}".format(self._PRIMARY_KEY_COLUMN_NAME, _INSERTION_TIMESTAMP_FIELD_NAME)
        create_table_query = u"CREATE TABLE {0} ({1})".format(self._table_name, columns)
        insert_query = u"INSERT INTO {0} VALUES(?, null)".format(self._table_name)
        with self._connection as conn:
            conn.execute(create_table_query)
            conn.execute(insert_query, (self._PRIMARY_KEY,))
