import pytest
from argparse import ArgumentParser
from code42cli.profile import profile


@pytest.fixture(autouse=True)
def username_setter(mocker):
    return mocker.patch("code42cli.profile.config.set_username")


@pytest.fixture(autouse=True)
def mark_as_set_function(mocker):
    return mocker.patch("code42cli.profile.config.mark_as_set_if_complete")


@pytest.fixture(autouse=True)
def authority_url_setter(mocker):
    return mocker.patch("code42cli.profile.config.set_authority_url")


@pytest.fixture(autouse=True)
def ignore_ssl_errors_setter(mocker):
    return mocker.patch("code42cli.profile.config.set_ignore_ssl_errors")


@pytest.fixture(autouse=True)
def password_setter(mocker):
    return mocker.patch("code42cli.profile.password.set_password_from_prompt")


@pytest.fixture(autouse=True)
def password_getter(mocker):
    return mocker.patch("code42cli.profile.password.get_password")


@pytest.fixture
def profile_not_set_state(mocker):
    profile_verifier = mocker.patch("code42cli.profile.config.profile_has_been_set")
    profile_verifier.return_value = False
    return profile_verifier


def _get_profile_parser():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    return subcommand_parser.choices.get("profile")


class TestCode42Profile(object):
    def test_get_password_when_is_none_returns_password_from_getpass(self, mocker, password_getter):
        password_getter.return_value = None
        mock_getpass = mocker.patch("code42cli.profile.password.get_password_from_prompt")
        mock_getpass.return_value = "Test Password"
        actual = profile.Code42Profile().get_password()
        assert actual == "Test Password"

    def test_get_password_return_password_from_password_get_password(self, password_getter):
        password_getter.return_value = "Test Password"
        actual = profile.Code42Profile().get_password()
        assert actual == "Test Password"


@pytest.fixture
def profile_is_set_state(mocker):
    profile_verifier = mocker.patch("code42cli.profile.config.profile_has_been_set")
    profile_verifier.return_value = True
    return profile_verifier


def test_init_adds_profile_subcommand_to_choices(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    assert subcommand_parser.choices.get("profile")


def test_init_adds_parser_that_can_parse_show_command(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["show"])


def test_init_adds_parser_that_can_parse_set_command(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    profile_parser.parse_args(
        ["set", "-s", "server-arg", "--set-password", "-u", "username-arg", "--enable-ssl-errors"]
    )


def test_get_profile_returns_object_from_config_profile(config_parser, config_profile):
    user = profile.get_profile()
    # Values from config_profile fixture
    assert (
        user.username == "test.username"
        and user.authority_url == "https://authority.example.com"
        and user.ignore_ssl_errors
    )


def test_set_profile_when_given_username_sets_username(
    config_parser, username_setter, profile_is_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    username_setter.assert_called_once_with("a.new.user@example.com")


def test_set_profile_when_given_authority_url_sets_authority_url(
    config_parser, authority_url_setter, profile_is_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "https://wwww.new.authority.example.com"])
    profile.set_profile(namespace)
    authority_url_setter.assert_called_once_with("https://wwww.new.authority.example.com")


def test_set_profile_when_given_enable_ssl_errors_sets_ignore_ssl_errors_to_true(
    config_parser, ignore_ssl_errors_setter, profile_is_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--enable-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(False)


def test_set_profile_when_given_disable_ssl_errors_sets_ignore_ssl_errors_to_false(
    config_parser, ignore_ssl_errors_setter, profile_is_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(True)


def test_set_profile_when_is_first_time_and_given_username_sets_username(
    config_parser,
    profile_not_set_state,
    username_setter,
    mark_as_set_function,
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-u", "user"]
    )
    profile.set_profile(namespace)
    username_setter.assert_called_once_with("user")


def test_set_profile_when_is_first_time_and_given_authority_sets_authority_url(
    config_parser,
    profile_not_set_state,
    authority_url_setter,
    mark_as_set_function,
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com"]
    )
    profile.set_profile(namespace)
    authority_url_setter.assert_called_once_with("https://wwww.new.authority.example.com")


def test_set_profile_calls_marks_as_set_if_complete(
    config_parser,
    profile_not_set_state,
    mark_as_set_function,
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    assert mark_as_set_function.call_count


def test_set_profile_when_given_set_password_arg_sets_password(
    config_parser, password_setter, profile_is_set_state
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--set-password"])
    profile.set_profile(namespace)
    assert password_setter.call_count
