import pytest

import code42cli.profile.password as password


@pytest.fixture
def keyring(mocker):
    return mocker.patch("code42cli._internal.profile.password.keyring")

@pytest.fixture
def getpass_function(mocker):
    return mocker.patch("code42cli.profile.password.getpass")


def test_get_password_uses_expected_service_name_and_username(
    keyring, config_profile
):
    with keyring:
        password.get_password()
        # See conftest.config_profile
        expected_service_name = "code42cli::https://authority.example.com"
        expected_username = "test.username"
        keyring.get_password.assert_called_once_with(expected_service_name, expected_username)


def test_get_password_when_password_is_none_returns_password_from_getpass(
    keyring, config_profile, getpass_function
):
    with keyring, getpass_function:
        keyring.get_password.return_value = None
        getpass_function.return_value = "test password"
        assert password.get_password() == "test password"


def test_get_password_when_password_is_not_none_returns_password(
    keyring, config_profile
):
    with keyring:
        keyring.get_password.return_value = "already stored password 123"
        assert password.get_password() == "already stored password 123"


def test_get_password_when_password_is_none_and_told_to_not_prompt_if_not_exists_returns_none(
    keyring, config_profile
):
    with keyring:
        keyring.get_password.return_value = None
        assert password.get_password(prompt_if_not_exists=False) is None


def test_set_password_uses_expected_service_name_username_and_password(
keyring, config_profile, getpass_function
):
    with keyring, getpass_function:
        getpass_function.return_value = "test password"
        password.set_password()
        # See conftest.config_profile
        expected_service_name = "code42cli::https://authority.example.com"
        expected_username = "test.username"
        keyring.set_password.assert_called_once_with(
            expected_service_name, expected_username, "test password"
        )
