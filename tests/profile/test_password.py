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


@pytest.fixture
def user_agreement(mocker):
    mock = mocker.patch("code42cli.profile.password.does_user_agree")
    mock.return_value = True
    return mock


@pytest.fixture
def user_disagreement(mocker):
    mock = mocker.patch("code42cli.profile.password.does_user_agree")
    mock.return_value = False
    return mock


@pytest.fixture
def file_opener(mocker):
    return mocker.patch("code42cli.profile.password.open_file")


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


def test_get_stored_password_when_keyring_returns_none_returns_password_from_file(
    keyring_password_getter, config_accessor, file_opener
):
    keyring_password_getter.return_value = None
    file_opener.return_value = "FileStoredPassword123!"
    assert password.get_stored_password("profile_name") == "FileStoredPassword123!"


def test_get_stored_password_when_keyring_throws_exception_returns_password_from_file(
    keyring_password_getter, config_accessor, file_opener
):
    def side_effect(*args):
        raise Exception()

    keyring_password_getter.side_effect = side_effect
    file_opener.return_value = "FileStoredPassword123!"
    assert password.get_stored_password("profile_name") == "FileStoredPassword123!"


def test_get_stored_password_when_not_in_keyring_or_file_returns_none(
    keyring_password_getter, config_accessor, file_opener
):
    keyring_password_getter.return_value = None
    file_opener.return_value = None
    assert not password.get_stored_password("profile_name")


def test_get_stored_password_when_not_in_keyring_and_getting_from_file_throws_returns_none(
    keyring_password_getter, config_accessor, file_opener
):
    keyring_password_getter.return_value = None

    def side_effect(*args):
        raise Exception()

    file_opener.side_effect = side_effect
    assert not password.get_stored_password("profile_name")


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


def test_set_password_when_not_found_in_keyring_after_set_and_user_agrees_stores_in_file(
    keyring_password_setter, config_accessor, keyring_password_getter, user_agreement, file_opener
):
    keyring_password_getter.return_value = None
    password.set_password("profile_name", "test_password")
    assert file_opener.call_count == 1


def test_set_password_when_not_found_in_keyring_after_set_and_user_disagrees_does_not_store(
    keyring_password_setter,
    config_accessor,
    keyring_password_getter,
    user_disagreement,
    file_opener,
):
    keyring_password_getter.return_value = None
    password.set_password("profile_name", "test_password")
    assert file_opener.call_count == 0


def test_set_password_when_keyring_throws_and_user_agrees_stores_in_file(
    keyring_password_setter, config_accessor, user_agreement, file_opener
):
    def side_effect(*args):
        raise Exception()

    keyring_password_setter.side_effect = side_effect
    password.set_password("profile_name", "test_password")
    assert file_opener.call_count == 1
