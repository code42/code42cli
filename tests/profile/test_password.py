import pytest

import code42cli.profile.password as password
from code42cli.profile.config import ConfigAccessor
from .conftest import PASSWORD_NAMESPACE
from ..conftest import setup_mock_accessor, create_profile_values_dict

_USERNAME = "test.username"


@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor)
    factory = mocker.patch("{0}.get_config_accessor".format(PASSWORD_NAMESPACE))
    factory.return_value = mock
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


def test_get_stored_password_when_given_profile_name_gets_profile_for_that_name(
    keyring_password_getter, config_accessor
):
    password.get_stored_password("profile_name")
    assert config_accessor.get_profile.call_args_list[0][0][0] == "profile_name"


def test_get_stored_password_returns_expected_password(
    keyring_password_getter, config_accessor, keyring_password_setter
):
    keyring_password_getter.return_value = "already stored password 123"
    assert password.get_stored_password("profile_name") == "already stored password 123"


def test_set_password_uses_expected_service_name_username_and_password(
    keyring_password_setter, config_accessor, keyring_password_getter
):
    keyring_password_getter.return_value = "test_password"
    values = create_profile_values_dict(username="test.username")
    setup_mock_accessor(config_accessor, "profile_name", values)
    password.set_password("profile_name", "test_password")
    expected_service_name = "code42cli::profile_name"
    expected_username = "test.username"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, expected_username, "test_password"
    )


def test_set_password_when_given_none_uses_password_from_default_profile(
    keyring_password_setter, config_accessor, keyring_password_getter
):
    keyring_password_getter.return_value = "test_password"
    values = create_profile_values_dict(username="test.username")
    setup_mock_accessor(config_accessor, "Default_Profile", values)
    config_accessor.name = "Default_Profile"
    password.set_password(None, "test_password")
    expected_service_name = "code42cli::Default_Profile"
    expected_username = "test.username"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, expected_username, "test_password"
    )
