import pytest
import c42sec.profile._password as password


@pytest.fixture
def keyring_password_getter(mocker):
    return mocker.patch("keyring.get_password")


@pytest.fixture
def keyring_password_setter(mocker):
    return mocker.patch("keyring.set_password")


def test_get_password_uses_expected_service_name_and_username(
    keyring_password_getter, config_profile
):
    password.get_password()
    # See conftest.config_profile
    expected_service_name = "c42sec::https://authority.example.com"
    expected_username = "test.username"
    keyring_password_getter.assert_called_once_with(expected_service_name, expected_username)


def test_set_password_uses_expected_service_name_and_username(
    keyring_password_setter, config_profile
):
    password.set_password("test password")
    # See conftest.config_profile
    expected_service_name = "c42sec::https://authority.example.com"
    expected_username = "test.username"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, expected_username, "test password"
    )
