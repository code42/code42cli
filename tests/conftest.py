import pytest

MOCK_TEST_DB_PATH = "test_path.db"


@pytest.fixture
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")
