import pytest
from argparse import ArgumentParser
from c42sec.profile import profile
from c42sec.profile._config import ConfigurationKeys


@pytest.fixture
def config_file(mocker):
    mock_config = mocker.patch("c42sec.profile.profile.get_config_profile")
    mock_config.return_value = {
        ConfigurationKeys.USERNAME_KEY: "test.username",
        ConfigurationKeys.AUTHORITY_KEY: "https://authority.example.com",
        ConfigurationKeys.IGNORE_SSL_ERRORS_KEY: True,
    }
    return mock_config


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
        ["set", "-s", "server-arg", "-p", "-u", "username-arg", "--ignore-ssl-errors"]
    )


def test_get_profile_returns_object_from_config_file(config_file):
    user = profile.get_profile()

    # Values from config_file fixture
    assert (
        user.username == "test.username"
        and user.authority_url == "https://authority.example.com"
        and user.ignore_ssl_errors
    )


def test_set_profile_when_given_username_sets_username(mocker):
    username_setter = mocker.patch("c42sec.profile.profile.set_username")
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    username_setter.assert_called_once_with("a.new.user@example.com")


def test_set_profile_when_given_authority_url_sets_authority_url(mocker):
    authority_url_setter = mocker.patch("c42sec.profile.profile.set_authority_url")
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "https://wwww.new.authority.example.com"])
    profile.set_profile(namespace)
    authority_url_setter.assert_called_once_with("https://wwww.new.authority.example.com")


def test_set_profile_when_given_ignore_ssl_errors_sets_ignore_ssl_errors(mocker):
    ignore_ssl_errors_setter = mocker.patch("c42sec.profile.profile.set_ignore_ssl_errors")
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--ignore-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(True)


def test_set_profile_when_given_password_sets_password_returned_from_getpass(mocker):
    password_setter = mocker.patch("c42sec.profile.profile.set_password")
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
