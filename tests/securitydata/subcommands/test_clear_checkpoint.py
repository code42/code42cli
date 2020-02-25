import pytest

from code42cli.securitydata.subcommands import clear_checkpoint as clearer


@pytest.fixture
def cursor_store(mocker):
    mock_init = mocker.patch(
        "code42cli.securitydata.cursor_store.AEDCursorStore.__init__"
    )
    mock_init.return_value = None
    mock = mocker.MagicMock()
    mock_new = mocker.patch(
        "code42cli.securitydata.cursor_store.AEDCursorStore.__new__"
    )
    mock_new.return_value = mock
    return mock


def test_clear_checkpoint_calls_cursor_store_reset(cursor_store):
    clearer.clear_checkpoint()
    assert cursor_store.reset.call_count == 1
