import pytest

import code42cli.profile.password as password
from code42cli.profile.config import ConfigAccessor
from .conftest import PASSWORD_NAMESPACE


_USERNAME = "test.username"

@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor)
    factory = mocker.patch("{0}.get_config_accessor".format(PASSWORD_NAMESPACE))
    factory.return_value = mock

    class MockConfigProfile(object):
        def __getitem__(self, item):
            return _USERNAME

    mock.get_profile.return_value = MockConfigProfile()
    return mock


@pytest.fixture
def keyring_password_getter(mocker):
    return mocker.patch("keyring.get_password")


@pytest.fixture(autouse=True)
def keyring_password_setter(mocker):
    return mocker.patch("keyring.set_password")


@pytest.fixture
def getpass_function(mocker):
    return mocker.patch("code42cli.profile.password.getpass")


def test_get_password_uses_expected_service_name_and_username(
    keyring_password_getter, config_accessor
):
    password.get_password("profile_name")
    expected_service_name = "code42cli::profile_name"
    keyring_password_getter.assert_called_once_with(expected_service_name, _USERNAME)


def test_get_password_returns_expected_password(
    keyring_password_getter, config_accessor, keyring_password_setter
):
    keyring_password_getter.return_value = "already stored password 123"
    assert password.get_password("profile_name") == "already stored password 123"


def test_set_password_from_prompt_uses_expected_service_name_username_and_password(
    keyring_password_setter, config_accessor, getpass_function
):
    getpass_function.return_value = "test password"
    password.set_password_from_prompt("profile_name")
    expected_service_name = "code42cli::profile_name"
    expected_username = "test.username"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, expected_username, "test password"
    )
