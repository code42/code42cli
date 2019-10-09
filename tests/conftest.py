import pytest

from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cursor_store import SecurityEventCursorStore


MOCK_TEST_DB_PATH = "test_path.db"


@pytest.fixture
def test_store(mocker, sqlite_connection, execute_function):
    store = SecurityEventCursorStore(MOCK_TEST_DB_PATH)
    store._connection = sqlite_connection
    return configure_store_with_mock_sqlite(
        store=store,
        mocker=mocker,
        sqlite_connection=sqlite_connection,
        execute_function=execute_function,
    )


@pytest.fixture
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")


@pytest.fixture
def execute_function(mocker):
    return mocker.MagicMock()


@pytest.fixture
def aed_cursor_store(mocker, sqlite_connection, execute_function):
    store = AEDCursorStore(MOCK_TEST_DB_PATH)
    return configure_store_with_mock_sqlite(
        store=store,
        mocker=mocker,
        sqlite_connection=sqlite_connection,
        execute_function=execute_function,
    )


def configure_store_with_mock_sqlite(
    store, mocker, sqlite_connection, execute_function
):
    store._connection = sqlite_connection
    with store._connection as conn:
        mock_cursor = mocker.MagicMock()
        mock_cursor.execute = execute_function
        conn.cursor.return_value = mock_cursor
        conn.execute = execute_function

    return store
