import pytest

from py42 import debug_level
from py42 import settings

from code42cli.sdk_client import create_sdk, validate_connection
from .conftest import create_mock_profile


@pytest.fixture
def mock_sdk_factory(mocker):
    return mocker.patch("py42.sdk.SDK.create_using_local_account")


@pytest.fixture
def error_sdk_factory(mocker, mock_sdk_factory):
    def side_effect():
        raise Exception()

    mock_sdk_factory.side_effect = side_effect
    return mock_sdk_factory


def test_create_sdk_when_py42_exception_occurs_causes_exit(error_sdk_factory):
    profile = create_mock_profile()
    with pytest.raises(SystemExit):
        create_sdk(profile, False)


def test_create_sdk_when_told_to_debug_turns_on_debug(mock_sdk_factory):
    profile = create_mock_profile()
    create_sdk(profile, True)
    assert settings.debug_level == debug_level.DEBUG


def test_validate_connection_when_creating_sdk_raises_returns_false(error_sdk_factory):
    assert not validate_connection("Test", "Password", "Authority")


def test_validate_connection_when_sdk_does_not_raise_returns_true(mock_sdk_factory):
    assert validate_connection("Test", "Password", "Authority")


def test_validate_connection_uses_given_credentials(mock_sdk_factory):
    assert validate_connection("Authority", "Test", "Password")
    mock_sdk_factory.assert_called_once_with("Authority", "Test", "Password")
