import pytest

from code42cli.securitydata.subcommands import clear_checkpoint as clearer
from ..conftest import SECURITYDATA_NAMESPACE

_CURSOR_STORE_NAMESPACE = "{0}.cursor_store".format(SECURITYDATA_NAMESPACE)


@pytest.fixture
def cursor_store(mocker):
    mock_init = mocker.patch("{0}.FileEventCursorStore.__init__".format(_CURSOR_STORE_NAMESPACE))
    mock_init.return_value = None
    mock = mocker.MagicMock()
    mock_new = mocker.patch("{0}.FileEventCursorStore.__new__".format(_CURSOR_STORE_NAMESPACE))
    mock_new.return_value = mock
    return mock


@pytest.fixture
def profile(mocker):
    class MockProfile(object):
        @property
        def name(self):
            return "AlreadySetProfileName"

    mock = mocker.patch(
        "{0}.subcommands.clear_checkpoint.get_profile".format(SECURITYDATA_NAMESPACE)
    )
    mock.return_value = MockProfile()
    return mock


def test_clear_checkpoint_when_given_profile_name_calls_cursor_store_resets(
    cursor_store, namespace
):
    namespace.profile_name = "Test"
    clearer.clear_checkpoint(namespace)
    assert cursor_store.replace_stored_insertion_timestamp.call_args[0][0] is None


def test_clear_checkpoint_calls_cursor_store_resets(cursor_store, namespace, profile):
    clearer.clear_checkpoint(namespace)
    assert cursor_store.replace_stored_insertion_timestamp.call_args[0][0] is None
