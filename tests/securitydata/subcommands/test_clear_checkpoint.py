import pytest

from .conftest import get_root_path
from code42cli.securitydata.subcommands import clear_checkpoint as clearer


def get_patch_path():
    return "{0}.cursor_store".format(get_root_path())


@pytest.fixture
def cursor_store(mocker):
    mock_init = mocker.patch("{0}.AEDCursorStore.__init__".format(get_patch_path()))
    mock_init.return_value = None
    mock = mocker.MagicMock()
    mock_new = mocker.patch("{0}.AEDCursorStore.__new__".format(get_patch_path()))
    mock_new.return_value = mock
    return mock


def test_clear_checkpoint_calls_cursor_store_reset(cursor_store):
    clearer.clear_checkpoint()
    assert cursor_store.reset.call_count == 1
