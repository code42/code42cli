import pytest

from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cursor_store import SecurityEventCursorStore


MOCK_TEST_DB_PATH = "test_path.db"


@pytest.fixture
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")
