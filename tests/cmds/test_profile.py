import pytest
from py42.exceptions import Py42MFARequiredError
from py42.sdk import SDKClient
from requests import Response
from requests.exceptions import HTTPError

from ..conftest import create_mock_profile
from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.main import cli


_SELECTED_PROFILE_NAME = "test_profile"


@pytest.fixture
def user_agreement(mocker):
    mock = mocker.patch("code42cli.cmds.profile.does_user_agree")
    mock.return_value = True
    return mocker


@pytest.fixture
def user_disagreement(mocker):
    mock = mocker.patch("code42cli.cmds.profile.does_user_agree")
    mock.return_value = False
    return mocker


@pytest.fixture
def mock_cliprofile_namespace(mocker):
    return mocker.patch("code42cli.cmds.profile.cliprofile")


@pytest.fixture(autouse=True)
def mock_getpass(mocker):
    mock = mocker.patch("code42cli.cmds.profile.getpass")
    mock.return_value = "newpassword"


@pytest.fixture
def mock_verify(mocker):
    return mocker.patch("code42cli.cmds.profile.create_sdk")


@pytest.fixture
def valid_connection(mocker, mock_verify):
    mock_sdk = mocker.MagicMock(spec=SDKClient)
    mock_verify.return_value = mock_sdk
    return mock_verify


@pytest.fixture
def invalid_connection(mock_verify):
    mock_verify.side_effect = LoggedCLIError("Problem connecting to server")
    return mock_verify


@pytest.fixture
def profile_name_selector(mocker):
    mock = mocker.patch("code42cli.cmds.profile.click.prompt")
    mock.return_value = _SELECTED_PROFILE_NAME
    return mock


def test_show_profile_outputs_profile_info(runner, mock_cliprofile_namespace, profile):
    profile.name = "testname"
    profile.authority_url = "example.com"
    profile.username = "foo"
    profile.disable_ssl_errors = True
    mock_cliprofile_namespace.get_profile.return_value = profile
    result = runner.invoke(cli, ["profile", "show"])
    assert "testname" in result.output
    assert "example.com" in result.output
    assert "foo" in result.output
    assert "A password is set" in result.output


def test_show_profile_when_password_set_outputs_password_note(
    runner, mock_cliprofile_namespace, profile
):
    mock_cliprofile_namespace.get_profile.return_value = profile
    mock_cliprofile_namespace.get_stored_password.return_value = None
    result = runner.invoke(cli, ["profile", "show"])
    assert "A password is set" not in result.output


def test_create_profile_if_user_sets_password_is_created(
    runner, user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_cliprofile_namespace.create_profile.assert_called_once_with(
        "foo", "bar", "baz", True
    )


def test_create_profile_if_user_does_not_set_password_is_created(
    runner, user_disagreement, mock_verify, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_cliprofile_namespace.create_profile.assert_called_once_with(
        "foo", "bar", "baz", True
    )


def test_create_profile_if_user_does_not_agree_does_not_save_password(
    runner, user_disagreement, mock_verify, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert not mock_cliprofile_namespace.set_password.call_count


def test_create_profile_if_credentials_invalid_password_not_saved(
    runner, user_agreement, invalid_connection, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    result = runner.invoke(
        cli, ["profile", "create", "-n", "foo", "-s", "bar", "-u", "baz"],
    )
    assert "Password not stored!" in result.output
    assert not mock_cliprofile_namespace.set_password.call_count


def test_create_profile_with_password_option_if_credentials_invalid_password_not_saved(
    runner, invalid_connection, mock_cliprofile_namespace
):
    password = "test_pass"
    mock_cliprofile_namespace.profile_exists.return_value = False
    result = runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--password",
            password,
        ],
    )
    assert "Password not stored!" in result.output
    assert not mock_cliprofile_namespace.set_password.call_count
    assert "Would you like to set a password?" not in result.output


def test_create_profile_if_credentials_valid_password_saved(
    runner, mocker, user_agreement, valid_connection, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    runner.invoke(cli, ["profile", "create", "-n", "foo", "-s", "bar", "-u", "baz"])
    mock_cliprofile_namespace.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )


def test_create_profile_with_password_option_if_credentials_valid_password_saved(
    runner, mocker, valid_connection, mock_cliprofile_namespace
):
    password = "test_pass"
    mock_cliprofile_namespace.profile_exists.return_value = False
    result = runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--password",
            password,
        ],
    )
    mock_cliprofile_namespace.set_password.assert_called_once_with(password, mocker.ANY)
    assert "Would you like to set a password?" not in result.output


def test_create_profile_stores_password_and_prints_message_when_user_requires_mfa(
    runner, mocker, mock_verify, mock_cliprofile_namespace
):
    mock_verify.side_effect = Py42MFARequiredError(HTTPError(response=Response()))
    result = runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "mfa",
            "-s",
            "bar",
            "-u",
            "baz",
            "--password",
            "pass",
        ],
    )
    assert "Multi-factor account detected." in result.output
    mock_cliprofile_namespace.set_password.assert_called_once_with("pass", mocker.ANY)


def test_create_profile_outputs_confirmation(
    runner, user_agreement, valid_connection, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    result = runner.invoke(
        cli,
        [
            "profile",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert "Successfully created profile 'foo'." in result.output


def test_update_profile_updates_existing_profile(
    runner, mock_cliprofile_namespace, user_agreement, valid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile
    runner.invoke(
        cli,
        [
            "profile",
            "update",
            "-n",
            name,
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_cliprofile_namespace.update_profile.assert_called_once_with(
        name, "bar", "baz", True
    )


def test_update_profile_updates_default_profile(
    runner, mock_cliprofile_namespace, user_agreement, valid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile
    runner.invoke(
        cli, ["profile", "update", "-s", "bar", "-u", "baz", "--disable-ssl-errors"],
    )
    mock_cliprofile_namespace.update_profile.assert_called_once_with(
        name, "bar", "baz", True
    )


def test_update_profile_updates_name_alone(
    runner, mock_cliprofile_namespace, user_agreement, valid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile
    runner.invoke(
        cli, ["profile", "update", "-u", "baz", "--disable-ssl-errors"],
    )
    mock_cliprofile_namespace.update_profile.assert_called_once_with(
        name, None, "baz", True
    )


def test_update_profile_if_user_does_not_agree_does_not_save_password(
    runner, mock_cliprofile_namespace, user_disagreement, invalid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile
    runner.invoke(
        cli,
        [
            "profile",
            "update",
            "-n",
            name,
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert not mock_cliprofile_namespace.set_password.call_count


def test_update_profile_if_credentials_invalid_password_not_saved(
    runner, user_agreement, invalid_connection, mock_cliprofile_namespace, profile
):
    name = "foo"
    profile.name = name
    profile.has_stored_password = False
    mock_cliprofile_namespace.get_profile.return_value = profile

    result = runner.invoke(
        cli,
        [
            "profile",
            "update",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert not mock_cliprofile_namespace.set_password.call_count
    assert "Password not stored!" in result.output


def test_update_profile_if_user_agrees_and_valid_connection_sets_password(
    runner, mocker, user_agreement, valid_connection, mock_cliprofile_namespace, profile
):
    name = "foo"
    profile.name = name
    profile.has_stored_password = False
    mock_cliprofile_namespace.get_profile.return_value = profile
    runner.invoke(
        cli,
        [
            "profile",
            "update",
            "-n",
            name,
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_cliprofile_namespace.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )


def test_update_profile_when_given_zero_args_prints_error_message(
    runner, mock_cliprofile_namespace, profile
):
    name = "foo"
    profile.name = name
    profile.ignore_ssl_errors = False
    mock_cliprofile_namespace.get_profile.return_value = profile
    result = runner.invoke(cli, ["profile", "update"])
    expected = (
        "Must provide at least one of `--username`, `--server`, `--password`, "
        "or `--disable-ssl-errors` when updating a profile."
    )
    assert "Profile 'foo' has been updated" not in result.output
    assert expected in result.output


def test_delete_profile_warns_if_deleting_default(runner, mock_cliprofile_namespace):
    mock_cliprofile_namespace.is_default_profile.return_value = True
    result = runner.invoke(cli, ["profile", "delete", "mockdefault"])
    assert "'mockdefault' is currently the default profile!" in result.output


def test_delete_profile_requires_profile_name_arg(runner, mock_cliprofile_namespace):
    result = runner.invoke(cli, ["profile", "delete"])
    assert "Error: Missing argument 'PROFILE_NAME'." in result.output
    assert mock_cliprofile_namespace.delete_profile.call_count == 0


def test_delete_profile_does_nothing_if_user_doesnt_agree(
    runner, user_disagreement, mock_cliprofile_namespace
):
    runner.invoke(cli, ["profile", "delete", "mockdefault"])
    assert mock_cliprofile_namespace.delete_profile.call_count == 0


def test_delete_profile_outputs_success(
    runner, mock_cliprofile_namespace, user_agreement
):
    result = runner.invoke(cli, ["profile", "delete", "mockdefault"])
    assert "Profile 'mockdefault' has been deleted." in result.output


def test_delete_all_warns_if_profiles_exist(runner, mock_cliprofile_namespace):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    result = runner.invoke(cli, ["profile", "delete-all"])
    assert "Are you sure you want to delete the following profiles?" in result.output
    assert "test1" in result.output
    assert "test2" in result.output


def test_delete_all_does_not_warn_if_assume_yes_flag(runner, mock_cliprofile_namespace):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    result = runner.invoke(cli, ["profile", "delete-all", "-y"])
    assert (
        "Are you sure you want to delete the following profiles?" not in result.output
    )
    assert "Profile 'test1' has been deleted." in result.output
    assert "Profile 'test2' has been deleted." in result.output


def test_delete_all_profiles_does_nothing_if_user_doesnt_agree(
    runner, user_disagreement, mock_cliprofile_namespace
):
    runner.invoke(cli, ["profile", "delete-all"])
    assert mock_cliprofile_namespace.delete_profile.call_count == 0


def test_delete_all_deletes_all_existing_profiles(
    runner, user_agreement, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    runner.invoke(cli, ["profile", "delete-all"])
    mock_cliprofile_namespace.delete_profile.assert_any_call("test1")
    mock_cliprofile_namespace.delete_profile.assert_any_call("test2")


def test_reset_pw_if_credentials_valid_password_saved(
    runner, mocker, user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_verify.return_value = True
    mock_cliprofile_namespace.profile_exists.return_value = False
    runner.invoke(cli, ["profile", "reset-pw"])
    mock_cliprofile_namespace.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )


def test_reset_pw_if_credentials_invalid_password_not_saved(
    runner, user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_verify.side_effect = Code42CLIError("Invalid credentials for user")
    mock_cliprofile_namespace.profile_exists.return_value = False
    runner.invoke(cli, ["profile", "reset-pw"])
    assert not mock_cliprofile_namespace.set_password.call_count


def test_reset_pw_uses_default_profile_when_not_given_one(
    runner, mocker, user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_verify.return_value = True
    mock_cliprofile_namespace.profile_exists.return_value = False
    mock_profile = create_mock_profile("one")
    mock_cliprofile_namespace.get_profile.return_value = mock_profile
    res = runner.invoke(cli, ["profile", "reset-pw"])
    mock_cliprofile_namespace.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )
    assert "Password updated for profile 'one'." in res.output


def test_list_profiles(runner, mock_cliprofile_namespace):
    profiles = [
        create_mock_profile("one"),
        create_mock_profile("two"),
        create_mock_profile("three"),
    ]
    mock_cliprofile_namespace.get_all_profiles.return_value = profiles
    result = runner.invoke(cli, ["profile", "list"])
    assert "one" in result.output
    assert "two" in result.output
    assert "three" in result.output


def test_list_profiles_when_no_profiles_outputs_no_profiles_message(
    runner, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.get_all_profiles.return_value = []
    result = runner.invoke(cli, ["profile", "list"])
    assert "No existing profile." in result.output


def test_use_profile(runner, mock_cliprofile_namespace, profile):
    result = runner.invoke(cli, ["profile", "use", profile.name])
    mock_cliprofile_namespace.switch_default_profile.assert_called_once_with(
        profile.name
    )
    assert f"{profile.name} has been set as the default profile." in result.output


def test_use_profile_when_not_given_profile_name_arg_sets_selected_profile_as_default(
    runner, mock_cliprofile_namespace, profile_name_selector
):
    runner.invoke(cli, ["profile", "use"])
    mock_cliprofile_namespace.switch_default_profile.assert_called_once_with(
        _SELECTED_PROFILE_NAME
    )


def test_select_profile_sets_selected_profile_as_default(
    runner, mock_cliprofile_namespace, profile_name_selector
):
    runner.invoke(cli, ["profile", "select"])
    mock_cliprofile_namespace.switch_default_profile.assert_called_once_with(
        _SELECTED_PROFILE_NAME
    )


def test_select_profile_outputs_expected_text(
    runner, mock_cliprofile_namespace, profile_name_selector
):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    result = runner.invoke(cli, ["profile", "select"])
    expected_prompt = "1. test1\n2. test2"
    expected_result_message = (
        f"{_SELECTED_PROFILE_NAME} has been set as the default profile."
    )
    assert expected_prompt in result.output
    assert expected_result_message in result.output
