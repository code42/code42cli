import code42cli.password as password
import pytest

_USERNAME = "test.username"


@pytest.fixture
def keyring_password_getter(mocker):
    return mocker.patch("keyring.get_password")


@pytest.fixture(autouse=True)
def keyring_password_setter(mocker):
    return mocker.patch("keyring.set_password")


@pytest.fixture(autouse=True)
def get_keyring(mocker):
    mock = mocker.patch("keyring.get_keyring")
    mock.return_value.priority = 10
    return mock


@pytest.fixture
def getpass_function(mocker):
    return mocker.patch("code42cli.password.getpass")


@pytest.fixture
def user_agreement(mocker):
    mock = mocker.patch("code42cli.password.does_user_agree")
    mock.return_value = True
    return mocker


@pytest.fixture
def user_disagreement(mocker):
    mock = mocker.patch("code42cli.password.does_user_agree")
    mock.return_value = False
    return mocker


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


def test_set_password_when_using_file_fallback_and_user_accepts_saves_password(
    profile, keyring_password_setter, keyring_password_getter, get_keyring, user_agreement
):
    keyring_password_getter.return_value = "test_password"
    profile.name = "profile_name"
    profile.username = "test.username"
    password.set_password(profile, "test_password")
    expected_service_name = "code42cli::profile_name"
    keyring_password_setter.assert_called_once_with(
        expected_service_name, profile.username, "test_password"
    )


def test_set_password_when_using_file_fallback_and_user_rejects_does_not_saves_password(
    profile, keyring_password_setter, get_keyring, user_disagreement
):
    get_keyring.return_value.priority = 0.5
    keyring_password_getter.return_value = "test_password"
    profile.name = "profile_name"
    profile.username = "test.username"
    password.set_password(profile, "test_password")
    assert not keyring_password_setter.call_count


def test_prompt_for_password_calls_getpass(getpass_function):
    password.get_password_from_prompt()
    assert getpass_function.call_count
