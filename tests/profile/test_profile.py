import pytest
from argparse import ArgumentParser
from c42sec.profile import profile
from c42sec.profile._config import ConfigurationKeys


@pytest.fixture
def config_file(mocker):
    mock_config = mocker.patch("c42sec.profile._config.get_config_profile")
    mock_config.return_value = {
        ConfigurationKeys.USERNAME_KEY: "test.username",
        ConfigurationKeys.AUTHORITY_KEY: "https://authority.example.com",
        ConfigurationKeys.IGNORE_SSL_ERRORS_KEY: "True",
    }
    return mock_config


@pytest.fixture
def username_setter(mocker):
    return mocker.patch("c42sec.profile._config.set_username")


@pytest.fixture
def authority_url_setter(mocker):
    return mocker.patch("c42sec.profile._config.set_authority_url")


@pytest.fixture
def ignore_ssl_errors_setter(mocker):
    return mocker.patch("c42sec.profile._config.set_ignore_ssl_errors")


@pytest.fixture
def password_setter(mocker):
    return mocker.patch("c42sec.profile._password.set_password")


@pytest.fixture
def profile_not_set_state(mocker):
    profile_verifier = mocker.patch("c42sec.profile._config.profile_has_been_set")
    profile_verifier.return_value = False
    return profile_verifier


def test_init_adds_profile_subcommand_to_choices():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    assert subcommand_parser.choices.get("profile")


def test_init_adds_parser_that_can_parse_show_command():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["show"])


def test_init_adds_parser_that_can_parse_set_command():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")

    # Commands that require a value will fail here if not provided
    assert profile_parser.parse_args(
        ["set", "-s", "server-arg", "-p", "-u", "username-arg", "--enable-ssl-errors"]
    )


def test_get_profile_returns_object_from_config_file(config_file):
    user = profile.get_profile()

    # Values from config_file fixture
    assert (
        user.username == "test.username"
        and user.authority_url == "https://authority.example.com"
        and user.ignore_ssl_errors
    )


def test_set_profile_when_given_username_sets_username(username_setter):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    username_setter.assert_called_once_with("a.new.user@example.com")


def test_set_profile_when_is_first_time_and_given_username_but_not_given_authority_url_fails(
    username_setter, profile_not_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    with pytest.raises(SystemExit):
        profile.set_profile(namespace)


def test_set_profile_when_is_first_time_and_given_username_but_not_given_authority_url_does_not_set(
    username_setter, profile_not_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    with pytest.raises(SystemExit):
        profile.set_profile(namespace)

    assert username_setter.call_args is None


def test_set_profile_when_is_first_time_and_given_authority_url_but_not_given_username_fails(
    authority_url_setter, profile_not_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "https://wwww.new.authority.example.com"])
    with pytest.raises(SystemExit):
        profile.set_profile(namespace)


def test_set_profile_when_is_first_time_and_given_authority_url_but_not_given_username_does_not_set(
    authority_url_setter, profile_not_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "https://wwww.new.authority.example.com"])
    with pytest.raises(SystemExit):
        profile.set_profile(namespace)

    assert authority_url_setter.call_args is None


def test_set_profile_when_given_authority_url_sets_authority_url(authority_url_setter):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "https://wwww.new.authority.example.com"])
    profile.set_profile(namespace)
    authority_url_setter.assert_called_once_with("https://wwww.new.authority.example.com")


def test_set_profile_when_given_enable_ssl_errors_sets_ignore_ssl_errors_to_true(ignore_ssl_errors_setter):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--enable-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(False)


def test_set_profile_when_given_disable_ssl_errors_sets_ignore_ssl_errors_to_false(ignore_ssl_errors_setter):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(True)


def test_set_profile_when_given_password_sets_password_returned_from_getpass(mocker, password_setter):
    getpass_function = mocker.patch("c42sec.profile.profile.getpass")
    getpass_function.return_value = "a New p@55w0rd"

    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-p"])
    profile.set_profile(namespace)
    password_setter.assert_called_once_with("a New p@55w0rd")


def _get_profile_parser():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    return subcommand_parser.choices.get("profile")
