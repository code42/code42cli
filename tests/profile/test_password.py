import pytest

import code42cli.profile.password as password


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
    keyring_password_getter, config_profile
):
    password.get_password()
    expected_service_name = "code42cli::https://authority.example.com"
    expected_username = "test.username"
    keyring_password_getter.assert_called_once_with(expected_service_name, expected_username)


def test_get_password_returns_expected_password(
    keyring_password_getter, config_profile, keyring_password_setter
):
    keyring_password_getter.return_value = "already stored password 123"
    assert password.get_password() == "already stored password 123"


def test_set_password_from_prompt_uses_expected_service_name_username_and_password(
    keyring_password_setter, config_profile, getpass_function
):
    getpass_function.return_value = "test password"
    password.set_password_from_prompt()
    expected_service_name = "code42cli::https://authority.example.com"
    expected_username = "test.username"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, expected_username, "test password"
    )
