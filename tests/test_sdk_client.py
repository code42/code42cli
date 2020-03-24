import pytest
import py42.sdk
import py42.sdk.settings.debug as debug

from code42cli.sdk_client import create_sdk, validate_connection
from .conftest import create_mock_profile


@pytest.fixture
def mock_sdk_factory(mocker):
    return mocker.patch("py42.sdk.from_local_account")


@pytest.fixture
def error_sdk_factory(mock_sdk_factory):
    def side_effect():
        raise Exception()

    mock_sdk_factory.side_effect = side_effect
    return mock_sdk_factory


def test_create_sdk_when_py42_exception_occurs_causes_exit(error_sdk_factory):
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    with pytest.raises(SystemExit):
        create_sdk(profile, False)


def test_create_sdk_when_told_to_debug_turns_on_debug(mock_sdk_factory):
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    create_sdk(profile, True)
    assert py42.sdk.settings.debug.level == debug.DEBUG


def test_validate_connection_when_creating_sdk_raises_returns_false(error_sdk_factory):
    assert not validate_connection("Test", "Password", "Authority")


def test_validate_connection_when_sdk_does_not_raise_returns_true(mock_sdk_factory):
    assert validate_connection("Test", "Password", "Authority")


def test_validate_connection_uses_given_credentials(mock_sdk_factory):
    assert validate_connection("Authority", "Test", "Password")
    mock_sdk_factory.assert_called_once_with("Authority", "Test", "Password")
