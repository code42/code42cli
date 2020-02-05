import pytest
from argparse import ArgumentParser
from c42sec.profile import profile


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
def password_getter(mocker):
    return mocker.patch("c42sec.profile._password.get_password")


@pytest.fixture
def profile_not_set_state(mocker):
    profile_verifier = mocker.patch("c42sec.profile._config.profile_has_been_set")
    profile_verifier.return_value = False
    return profile_verifier


@pytest.fixture
def profile_is_set_state(mocker):
    profile_verifier = mocker.patch("c42sec.profile._config.profile_has_been_set")
    profile_verifier.return_value = True
    return profile_verifier


@pytest.fixture
def getpass_function(mocker):
    return mocker.patch("c42sec.profile.profile.getpass")


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


def test_get_profile_returns_object_from_config_file(config_profile):
    user = profile.get_profile()

    # Values from config_file fixture
    assert (
        user.username == "test.username"
        and user.authority_url == "https://authority.example.com"
        and user.ignore_ssl_errors
    )


def test_set_profile_when_given_username_sets_username(username_setter, password_getter):
    password_getter.return_value = "Something"  # Needed or else it prompts getpass
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


def test_set_profile_when_is_first_time_and_given_both_authority_and_username_sets_username(
    profile_not_set_state, username_setter, password_getter
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    username_setter.assert_called_once_with("user")


def test_set_profile_when_is_first_time_and_given_both_authority_and_username_sets_authority_url(
    profile_not_set_state, authority_url_setter, password_getter
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    authority_url_setter.assert_called_once_with("https://wwww.new.authority.example.com")


def test_set_profile_when_given_authority_url_sets_authority_url(authority_url_setter):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "https://wwww.new.authority.example.com"])
    profile.set_profile(namespace)
    authority_url_setter.assert_called_once_with("https://wwww.new.authority.example.com")


def test_set_profile_when_given_enable_ssl_errors_sets_ignore_ssl_errors_to_true(
    ignore_ssl_errors_setter
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--enable-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(False)


def test_set_profile_when_given_disable_ssl_errors_sets_ignore_ssl_errors_to_false(
    ignore_ssl_errors_setter
):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    ignore_ssl_errors_setter.assert_called_once_with(True)


def test_set_profile_when_given_password_sets_password_returned_from_getpass(
    getpass_function, password_setter
):
    getpass_function.return_value = "a New p@55w0rd"
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-p"])
    profile.set_profile(namespace)
    password_setter.assert_called_once_with("a New p@55w0rd")


def test_set_profile_when_given_username_but_username_does_not_have_stored_password_and_not_given_pflag_and_profile_is_set_sets_password_returned_from_getpass(
    mocker, getpass_function, password_setter, profile_is_set_state
):
    password_getter = mocker.patch("c42sec.profile._password.get_password")
    password_getter.return_value = None
    getpass_function.return_value = "a New p@55w0rd"
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    password_setter.assert_called_once_with("a New p@55w0rd")


def _get_profile_parser():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    return subcommand_parser.choices.get("profile")
