import pytest

from tests.securitydata.conftest import ROOT_PATH
from code42cli.securitydata.subcommands import clear_checkpoint as clearer


_CURSOR_STORE_PATH = "{0}.cursor_store".format(ROOT_PATH)


@pytest.fixture
def cursor_store(mocker):
    mock_init = mocker.patch("{0}.AEDCursorStore.__init__".format(_CURSOR_STORE_PATH))
    mock_init.return_value = None
    mock = mocker.MagicMock()
    mock_new = mocker.patch("{0}.AEDCursorStore.__new__".format(_CURSOR_STORE_PATH))
    mock_new.return_value = mock
    return mock


def test_clear_checkpoint_calls_cursor_store_reset(cursor_store):
    clearer.clear_checkpoint()
    assert cursor_store.reset.call_count == 1
