from argparse import ArgumentParser
import pytest

from code42cli.profile import profile
from code42cli.profile.config import ConfigAccessor
from .conftest import PASSWORD_NAMESPACE, PROFILE_NAMESPACE


@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor)
    factory = mocker.patch("{0}.profile.get_config_accessor".format(PROFILE_NAMESPACE))
    factory.return_value = mock
    return mock


@pytest.fixture(autouse=True)
def password_setter(mocker):
    return mocker.patch("{0}.set_password_from_prompt".format(PASSWORD_NAMESPACE))


@pytest.fixture(autouse=True)
def password_getter(mocker):
    return mocker.patch("{0}.get_password".format(PASSWORD_NAMESPACE))


@pytest.fixture(autouse=True)
def input_function(mocker):
    return mocker.patch("{0}.profile.get_input".format(PROFILE_NAMESPACE))


def _get_profile_parser():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    return subcommand_parser.choices.get("profile")


def create_profile():
    class MockSection(object):
        name = "TEST"

        def get(*args):
            pass

    return profile.Code42Profile(MockSection())


class TestCode42Profile(object):
    def test_get_password_when_is_none_returns_password_from_getpass(self, mocker, password_getter):
        password_getter.return_value = None
        mock_getpass = mocker.patch("{0}.get_password_from_prompt".format(PASSWORD_NAMESPACE))
        mock_getpass.return_value = "Test Password"
        actual = create_profile().get_password()
        assert actual == "Test Password"

    def test_get_password_return_password_from_password_get_password(self, password_getter):
        password_getter.return_value = "Test Password"
        actual = create_profile().get_password()
        assert actual == "Test Password"


def test_init_adds_profile_subcommand_to_choices(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    assert subcommand_parser.choices.get("profile")


def test_init_adds_parser_that_can_parse_show_command(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["show", "--profile", "name"])


def test_init_adds_parser_that_can_parse_set_command(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    profile_parser.parse_args(
        ["set", "-s", "server-arg", "-u", "username-arg", "--enable-ssl-errors"]
    )


def test_init_add_parser_that_can_parse_list_command():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["list"])


def test_init_add_parser_that_can_parse_use_command():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["use", "name"])


def test_get_profile_returns_object_from_config_profile(mocker, config_accessor):
    expected = mocker.MagicMock()
    config_accessor.get_profile.return_value = expected
    user = profile.get_profile()
    assert user._profile == expected


def test_set_profile_when_given_username_sets_username(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_username.call_args[0][0] == "a.new.user@example.com"


def test_set_profile_when_given_profile_name_sets_username_for_profile(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--profile", "profileA", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_username.call_args[0][0] == "a.new.user@example.com"
    assert config_accessor.set_username.call_args[0][1] == "profileA"


def test_set_profile_when_given_authority_sets_authority(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "-s", "example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_authority_url.call_args[0][0] == "example.com"


def test_set_profile_when_given_profile_name_sets_authority_for_profile(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--profile", "profileA", "-s", "example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_authority_url.call_args[0][0] == "example.com"
    assert config_accessor.set_authority_url.call_args[0][1] == "profileA"


def test_set_profile_when_given_enable_ssl_errors_sets_ignore_ssl_errors_to_true(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--enable-ssl-errors"])
    profile.set_profile(namespace)
    assert config_accessor.set_ignore_ssl_errors.call_args[0][0] == False


def test_set_profile_when_given_disable_ssl_errors_sets_ignore_ssl_errors_to_true(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    assert config_accessor.set_ignore_ssl_errors.call_args[0][0] == True


def test_set_profile_when_given_disable_ssl_errors_and_profile_name_sets_ignore_ssl_errors_to_true_for_profile(config_accessor):
    parser = _get_profile_parser()
    namespace = parser.parse_args(["set", "--profile", "profileA", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    assert config_accessor.set_ignore_ssl_errors.call_args[0][0] == True
    assert config_accessor.set_ignore_ssl_errors.call_args[0][1] == "profileA"


def test_set_profile_when_to_store_password_prompts_for_storing_password(mocker, config_accessor, input_function):
    input_function.return_value = "y"
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password_from_prompt")
    parser = _get_profile_parser()
    namespace = parser.parse_args(
             ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
         )
    profile.set_profile(namespace)
    assert mock_set_password_function.call_count


def test_set_profile_when_told_to_store_password_using_capital_y_prompts_for_storing_password(
    mocker, config_accessor, input_function
):
    input_function.return_value = "Y"
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password_from_prompt")
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    assert mock_set_password_function.call_count


def test_set_profile_when_told_not_to_store_password_prompts_for_storing_password(
    mocker, config_accessor, input_function
):
    input_function.return_value = "n"
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password_from_prompt")
    parser = _get_profile_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    assert not mock_set_password_function.call_count


def test_prompt_for_password_reset_calls_password_set_password_from_prompt(mocker, namespace):
    namespace.profile_name = "profile name"
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password_from_prompt")
    profile.prompt_for_password_reset(namespace)
    assert mock_set_password_function.call_count
