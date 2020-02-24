import pytest

from code42.subcommands.securitydata.clear_checkpoint import clear_checkpoint


@pytest.fixture
def cursor_store(mocker):
    mock_init = mocker.patch("code42._internal.securitydata.cursor_store.AEDCursorStore.__init__")
    mock_init.return_value = None
    mock = mocker.MagicMock()
    mock_new = mocker.patch("code42._internal.securitydata.cursor_store.AEDCursorStore.__new__")
    mock_new.return_value = mock
    return mock


def test_clear_checkpoint_calls_cursor_store_reset(cursor_store):
    clear_checkpoint()
    assert cursor_store.reset.call_count == 1
