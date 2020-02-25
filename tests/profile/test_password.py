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
    # See conftest.config_profile
    expected_service_name = "code42cli::https://authority.example.com"
    expected_username = "test.username"
    keyring_password_getter.assert_called_once_with(expected_service_name, expected_username)


def test_get_password_when_password_is_none_returns_password_from_getpass(
    keyring_password_getter, config_profile, getpass_function
):
    keyring_password_getter.return_value = None
    getpass_function.return_value = "test password"
    assert password.get_password() == "test password"


def test_get_password_when_password_is_not_none_returns_password(
    keyring_password_getter, config_profile, keyring_password_setter
):
    keyring_password_getter.return_value = "already stored password 123"
    assert password.get_password() == "already stored password 123"


def test_get_password_when_password_is_none_and_told_to_not_prompt_if_not_exists_returns_none(
    keyring_password_getter, config_profile
):
    keyring_password_getter.return_value = None
    assert password.get_password(prompt_if_not_exists=False) is None


def test_set_password_uses_expected_service_name_username_and_password(
    keyring_password_setter, config_profile, getpass_function
):
    getpass_function.return_value = "test password"
    password.set_password()
    # See conftest.config_profile
    expected_service_name = "code42cli::https://authority.example.com"
    expected_username = "test.username"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, expected_username, "test password"
    )
