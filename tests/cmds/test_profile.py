import pytest
from py42.sdk import SDKClient

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
            "True",
        ],
    )
    mock_cliprofile_namespace.create_profile.assert_called_once_with(
        "foo", "bar", "baz", True, None
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
            "True",
            "--use-v2-file-events",
            "True",
        ],
    )
    mock_cliprofile_namespace.create_profile.assert_called_once_with(
        "foo", "bar", "baz", True, True
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
            "True",
        ],
    )
    assert not mock_cliprofile_namespace.set_password.call_count


def test_create_profile_if_credentials_invalid_password_not_saved(
    runner, user_agreement, invalid_connection, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    result = runner.invoke(
        cli,
        ["profile", "create", "-n", "foo", "-s", "bar", "-u", "baz"],
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
            "True",
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
            "True",
        ],
    )
    mock_cliprofile_namespace.update_profile.assert_called_once_with(
        name, "bar", "baz", True, None
    )


def test_update_profile_updates_default_profile(
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
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
            "True",
            "--use-v2-file-events",
            "True",
        ],
    )
    mock_cliprofile_namespace.update_profile.assert_called_once_with(
        name, "bar", "baz", True, True
    )


def test_update_profile_updates_name_alone(
    runner, mock_cliprofile_namespace, user_agreement, valid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile
    runner.invoke(
        cli,
        ["profile", "update", "-u", "baz", "--disable-ssl-errors", "True"],
    )
    mock_cliprofile_namespace.update_profile.assert_called_once_with(
        name, None, "baz", True, None
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
            "True",
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
            "True",
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
            "True",
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
    profile.ignore_ssl_errors = "False"
    mock_cliprofile_namespace.get_profile.return_value = profile
    result = runner.invoke(cli, ["profile", "update"])
    expected = (
        "Must provide at least one of `--username`, `--server`, `--password`, "
        "`--use-v2-file-events` or `--disable-ssl-errors` when updating a profile."
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


def test_delete_profile_raises_CLIError_when_profile_does_not_exist(runner):
    result = runner.invoke(cli, ["profile", "delete", "not_a_real_profile"])
    assert result.output == "Error: Profile 'not_a_real_profile' does not exist.\n"


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


def test_use_profile_when_not_given_profile_name_outputs_expected_text(
    runner, mock_cliprofile_namespace, profile_name_selector
):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    result = runner.invoke(cli, ["profile", "use"])
    expected_prompt = "1. test1\n2. test2"
    expected_result_message = "test_profile has been set as the default profile."
    assert expected_prompt in result.output
    assert expected_result_message in result.output


def test_totp_option_passes_token_to_sdk_on_profile_cmds_that_init_sdk(
    runner, mocker, mock_cliprofile_namespace, cli_state
):
    totp1 = "123456"
    totp2 = "234567"
    mock_create_sdk = mocker.patch("code42cli.cmds.profile.create_sdk")
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
            "--password",
            "testpass",
            "--totp",
            totp1,
        ],
        obj=cli_state,
    )
    runner.invoke(
        cli,
        [
            "profile",
            "update",
            "-n",
            "foo",
            "--password",
            "updatedpass",
            "--totp",
            totp2,
        ],
        obj=cli_state,
    )
    assert mock_create_sdk.call_args_list[0][1]["totp"] == totp1
    assert mock_create_sdk.call_args_list[1][1]["totp"] == totp2


def test_debug_option_passed_to_sdk_on_profile_cmds_that_init_sdk(
    runner, mocker, mock_cliprofile_namespace, cli_state
):
    mock_create_sdk = mocker.patch("code42cli.cmds.profile.create_sdk")
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
            "--password",
            "testpass",
            "--debug",
        ],
        obj=cli_state,
    )
    runner.invoke(
        cli,
        ["profile", "update", "-n", "foo", "--password", "updatedpass", "--debug"],
        obj=cli_state,
    )
    assert mock_create_sdk.call_args_list[0][1]["is_debug_mode"] is True
    assert mock_create_sdk.call_args_list[1][1]["is_debug_mode"] is True
