import pytest

import code42cli.password as password
from code42cli.config import ConfigAccessor
from .conftest import setup_mock_accessor, create_profile_values_dict

_USERNAME = "test.username"


@pytest.fixture
def keyring_password_getter(mocker):
    return mocker.patch("keyring.get_password")


@pytest.fixture(autouse=True)
def keyring_password_setter(mocker):
    return mocker.patch("keyring.set_password")


@pytest.fixture
def getpass_function(mocker):
    return mocker.patch("code42cli.password.getpass")


def test_get_stored_password_when_given_profile_name_gets_profile_for_that_name(
    profile, keyring_password_getter
):
    profile.name = "foo"
    profile.username = "bar"
    service_name = "code42cli::{}".format(profile.name)
    password.get_stored_password(profile)
    keyring_password_getter.assert_called_once_with(service_name, profile.username)


def test_get_stored_password_returns_expected_password(
    profile, keyring_password_getter, keyring_password_setter
):
    keyring_password_getter.return_value = "already stored password 123"
    assert password.get_stored_password(profile) == "already stored password 123"


def test_set_password_uses_expected_service_name_username_and_password(
    profile, keyring_password_setter, keyring_password_getter
):
    keyring_password_getter.return_value = "test_password"
    profile.name = "profile_name"
    profile.username = "test.username"
    password.set_password(profile, "test_password")
    expected_service_name = "code42cli::profile_name"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, profile.username, "test_password"
    )


def test_prompt_for_password_calls_getpass(getpass_function):
    password.get_password_from_prompt()
    assert getpass_function.call_count
