from argparse import ArgumentParser

import pytest

from code42cli.profile import profile
from code42cli.profile.config import ConfigAccessor
from .conftest import PASSWORD_NAMESPACE, PROFILE_NAMESPACE
from ..conftest import MockSection, create_mock_profile


@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor, name="Config Accessor")
    factory = mocker.patch("{0}.profile.get_config_accessor".format(PROFILE_NAMESPACE))
    factory.return_value = mock
    return mock


@pytest.fixture(autouse=True)
def password_setter(mocker):
    return mocker.patch("{0}.set_password".format(PASSWORD_NAMESPACE))


@pytest.fixture(autouse=True)
def password_getter(mocker):
    return mocker.patch("{0}.get_stored_password".format(PASSWORD_NAMESPACE))


@pytest.fixture(autouse=True)
def input_function(mocker):
    return mocker.patch("{0}.profile.get_input".format(PROFILE_NAMESPACE))


def _get_arg_parser():
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    return subcommand_parser.choices.get("profile")


class TestCode42Profile(object):
    def test_get_password_when_is_none_returns_password_from_getpass(self, mocker, password_getter):
        password_getter.return_value = None
        mock_getpass = mocker.patch("{0}.get_password_from_prompt".format(PASSWORD_NAMESPACE))
        mock_getpass.return_value = "Test Password"
        actual = create_mock_profile().get_password()
        assert actual == "Test Password"

    def test_get_password_return_password_from_password_get_password(self, password_getter):
        password_getter.return_value = "Test Password"
        actual = create_mock_profile().get_password()
        assert actual == "Test Password"


def test_init_adds_profile_subcommand_to_choices(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    assert subcommand_parser.choices.get("profile")


def test_init_adds_parser_that_can_parse_show_command_without_profile(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["show"])


def test_init_adds_parser_that_can_parse_show_command_with_profile(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    assert profile_parser.parse_args(["show", "--profile", "name"])


def test_init_adds_parser_that_can_parse_set_command_without_profile(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    profile_parser.parse_args(
        ["set", "-s", "server-arg", "-u", "username-arg", "--enable-ssl-errors"]
    )


def test_init_adds_parser_that_can_parse_set_command_with_profile(config_accessor):
    subcommand_parser = ArgumentParser().add_subparsers()
    profile.init(subcommand_parser)
    profile_parser = subcommand_parser.choices.get("profile")
    profile_parser.parse_args(
        [
            "set",
            "--profile",
            "ProfileName",
            "-s",
            "server-arg",
            "-u",
            "username-arg",
            "--enable-ssl-errors",
        ]
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
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_username.call_args[0][0] == "a.new.user@example.com"


def test_set_profile_when_given_profile_name_sets_username_for_profile(config_accessor):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "--profile", "profileA", "-u", "a.new.user@example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_username.call_args[0][0] == "a.new.user@example.com"
    assert config_accessor.set_username.call_args[0][1] == "profileA"


def test_set_profile_when_given_authority_sets_authority(config_accessor):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "-s", "example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_authority_url.call_args[0][0] == "example.com"


def test_set_profile_when_given_profile_name_sets_authority_for_profile(config_accessor):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "--profile", "profileA", "-s", "example.com"])
    profile.set_profile(namespace)
    assert config_accessor.set_authority_url.call_args[0] == ("example.com", "profileA")


def test_set_profile_when_given_enable_ssl_errors_sets_ignore_ssl_errors_to_true(config_accessor):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "--enable-ssl-errors"])
    profile.set_profile(namespace)
    assert config_accessor.set_ignore_ssl_errors.call_args[0][0] == False


def test_set_profile_when_given_disable_ssl_errors_sets_ignore_ssl_errors_to_true(config_accessor):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    assert config_accessor.set_ignore_ssl_errors.call_args[0][0] == True


def test_set_profile_when_given_disable_ssl_errors_and_profile_name_sets_ignore_ssl_errors_to_true_for_profile(
    config_accessor
):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["set", "--profile", "profileA", "--disable-ssl-errors"])
    profile.set_profile(namespace)
    assert config_accessor.set_ignore_ssl_errors.call_args[0] == (True, "profileA")


def test_set_profile_when_to_store_password_prompts_for_storing_password(
    mocker, config_accessor, input_function
):
    mock_successful_connection = mocker.patch("code42cli.profile.profile.validate_connection")
    mock_successful_connection.return_value = True
    input_function.return_value = "y"
    mocker.patch("code42cli.profile.password.get_password_from_prompt")
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password")
    parser = _get_arg_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    assert mock_set_password_function.call_count


def test_set_profile_when_told_not_to_store_password_does_not_prompt_for_storing_password(
    mocker, config_accessor, input_function
):
    input_function.return_value = "n"
    mocker.patch("code42cli.profile.password.get_password_from_prompt")
    parser = _get_arg_parser()
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password")
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    profile.set_profile(namespace)
    assert not mock_set_password_function.call_count


def test_set_profile_when_told_to_store_password_but_connection_fails_exits(
    mocker, config_accessor, input_function
):
    mock_successful_connection = mocker.patch("code42cli.profile.profile.validate_connection")
    mock_successful_connection.return_value = False
    input_function.return_value = "y"
    mocker.patch("code42cli.profile.password.get_password_from_prompt")
    parser = _get_arg_parser()
    namespace = parser.parse_args(
        ["set", "-s", "https://wwww.new.authority.example.com", "-u", "user"]
    )
    with pytest.raises(SystemExit):
        profile.set_profile(namespace)


def test_prompt_for_password_reset_when_connection_fails_does_not_reset_password(
    mocker, config_accessor, input_function
):
    mock_successful_connection = mocker.patch("code42cli.profile.profile.validate_connection")
    mock_successful_connection.return_value = False
    input_function.return_value = "y"
    mocker.patch("code42cli.profile.password.get_password_from_prompt")
    parser = _get_arg_parser()
    namespace = parser.parse_args(["reset-pw", "--profile", "Test"])
    with pytest.raises(SystemExit):
        profile.prompt_for_password_reset(namespace)


def test_prompt_for_password_when_not_given_profile_name_calls_set_password_with_default_profile(
    mocker, config_accessor, input_function
):
    default_profile = MockSection()
    config_accessor.get_profile.return_value = default_profile
    mock_successful_connection = mocker.patch("code42cli.profile.profile.validate_connection")
    mock_successful_connection.return_value = True
    input_function.return_value = "y"
    password_prompt = mocker.patch("code42cli.profile.password.get_password_from_prompt")
    password_prompt.return_value = "new password"
    parser = _get_arg_parser()
    namespace = parser.parse_args(["reset-pw"])
    mock_set_password_function = mocker.patch("code42cli.profile.password.set_password")
    profile.prompt_for_password_reset(namespace)
    mock_set_password_function.assert_called_once_with(default_profile.name, "new password")


def test_list_profiles_when_no_profiles_prints_error(mocker, config_accessor):
    config_accessor.get_all_profiles.return_value = []
    mock_error_printer = mocker.patch("code42cli.util.print_error")
    parser = _get_arg_parser()
    namespace = parser.parse_args(["list"])
    profile.list_profiles(namespace)
    mock_error_printer.assert_called_once_with("No existing profile.")


def test_list_profiles_when_profiles_exists_does_not_print_error(mocker, config_accessor):
    config_accessor.get_all_profiles.return_value = [MockSection()]
    mock_error_printer = mocker.patch("code42cli.util.print_error")
    parser = _get_arg_parser()
    namespace = parser.parse_args(["list"])
    profile.list_profiles(namespace)
    assert not mock_error_printer.call_count


def test_use_profile_when_switching_fails_causes_exit(config_accessor):
    def side_effect(*args):
        raise Exception()
    config_accessor.switch_default_profile.side_effect = side_effect
    parser = _get_arg_parser()
    namespace = parser.parse_args(["use", "TestProfile"])
    with pytest.raises(SystemExit):
        profile.use_profile(namespace)


def test_use_profile_calls_accessor_with_expected_profile_name(config_accessor):
    parser = _get_arg_parser()
    namespace = parser.parse_args(["use", "TestProfile"])
    profile.use_profile(namespace)
    config_accessor.switch_default_profile.assert_called_once_with("TestProfile")
