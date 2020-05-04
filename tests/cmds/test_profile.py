import pytest
import logging

import code42cli.cmds.profile as profilecmd
from code42cli import PRODUCT_NAME
from ..conftest import create_mock_profile


@pytest.fixture
def user_agreement(mocker):
    mock = mocker.patch("{}.cmds.profile.does_user_agree".format(PRODUCT_NAME))
    mock.return_value = True
    return mocker


@pytest.fixture
def user_disagreement(mocker):
    mock = mocker.patch("{}.cmds.profile.does_user_agree".format(PRODUCT_NAME))
    mock.return_value = False
    return mocker


@pytest.fixture
def mock_cliprofile_namespace(mocker):
    return mocker.patch("{}.cmds.profile.cliprofile".format(PRODUCT_NAME))


@pytest.fixture(autouse=True)
def mock_getpass(mocker):
    mock = mocker.patch("{}.cmds.profile.getpass".format(PRODUCT_NAME))
    mock.return_value = "newpassword"


@pytest.fixture
def mock_verify(mocker):
    return mocker.patch("{}.cmds.profile.validate_connection".format(PRODUCT_NAME))


@pytest.fixture
def valid_connection(mock_verify):
    mock_verify.return_value = True
    return mock_verify


@pytest.fixture
def invalid_connection(mock_verify):
    mock_verify.return_value = False
    return mock_verify


def test_show_profile_outputs_profile_info(caplog, mock_cliprofile_namespace, profile):
    profile.name = "testname"
    profile.authority_url = "example.com"
    profile.username = "foo"
    profile.disable_ssl_errors = True
    mock_cliprofile_namespace.get_profile.return_value = profile
    profilecmd.show_profile(profile)
    assert "testname" in caplog.text
    assert "example.com" in caplog.text
    assert "foo" in caplog.text
    assert "A password is set" in caplog.text


def test_show_profile_when_password_set_outputs_password_note(
    capsys, mock_cliprofile_namespace, profile
):
    mock_cliprofile_namespace.get_profile.return_value = profile
    mock_cliprofile_namespace.get_stored_password.return_value = None
    profilecmd.show_profile(profile)
    capture = capsys.readouterr()
    assert "A password is set" not in capture.out


def test_create_profile_if_user_sets_password_is_created(
    user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    mock_cliprofile_namespace.create_profile.assert_called_once_with("foo", "bar", "baz", True)


def test_create_profile_if_user_does_not_set_password_is_created(
    user_disagreement, mock_verify, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    mock_cliprofile_namespace.create_profile.assert_called_once_with("foo", "bar", "baz", True)


def test_create_profile_if_user_does_not_agree_does_not_save_password(
    user_disagreement, mock_verify, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    assert not mock_cliprofile_namespace.set_password.call_count


def test_create_profile_if_credentials_invalid_password_not_saved(
    user_agreement, invalid_connection, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    success = False
    try:
        profilecmd.create_profile("foo", "bar", "baz", True)
    except SystemExit:
        success = True
        assert not mock_cliprofile_namespace.set_password.call_count
    assert success


def test_create_profile_if_credentials_valid_password_saved(
    mocker, user_agreement, valid_connection, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    mock_cliprofile_namespace.set_password.assert_called_once_with("newpassword", mocker.ANY)


def test_create_profile_outputs_confirmation(
    user_agreement, valid_connection, mock_cliprofile_namespace, caplog,
):
    with caplog.at_level(logging.INFO):
        mock_cliprofile_namespace.profile_exists.return_value = False
        profilecmd.create_profile("foo", "bar", "baz", True)
        assert "Successfully created profile 'foo'." in caplog.text


def test_update_profile_updates_existing_profile(
    mock_cliprofile_namespace, user_agreement, valid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile

    profilecmd.update_profile(name=name, server="bar", username="baz", disable_ssl_errors=True)
    mock_cliprofile_namespace.update_profile.assert_called_once_with(name, "bar", "baz", True)


def test_update_profile_if_user_does_not_agree_does_not_save_password(
    mock_cliprofile_namespace, user_disagreement, invalid_connection, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile
    assert not mock_cliprofile_namespace.set_password.call_count


def test_update_profile_if_credentials_invalid_password_not_saved(
    user_agreement, invalid_connection, mock_cliprofile_namespace, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile

    success = False
    try:
        profilecmd.create_profile("foo", "bar", "baz", True)
    except SystemExit:
        success = True
        assert not mock_cliprofile_namespace.set_password.call_count
    assert success


def test_update_profile_if_user_agrees_and_valid_connection_sets_password(
    mocker, user_agreement, valid_connection, mock_cliprofile_namespace, profile
):
    name = "foo"
    profile.name = name
    mock_cliprofile_namespace.get_profile.return_value = profile

    profilecmd.update_profile(name, "bar", "baz", True)
    mock_cliprofile_namespace.set_password.assert_called_once_with("newpassword", mocker.ANY)


def test_delete_profile_warns_if_deleting_default(
    caplog, user_agreement, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.is_default_profile.return_value = True
    with caplog.at_level(logging.ERROR):
        profilecmd.delete_profile("mockdefault")
        assert "mockdefault is currently the default profile!" in caplog.text


def test_delete_all_warns_if_profiles_exist(caplog, user_agreement, mock_cliprofile_namespace):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    with caplog.at_level(logging.INFO):
        profilecmd.delete_all_profiles()
        assert "Are you sure you want to delete the following profiles?" in caplog.text
        assert "test1" in caplog.text
        assert "test2" in caplog.text


def test_delete_profile_does_nothing_if_user_doesnt_agree(
    user_disagreement, mock_cliprofile_namespace
):
    profilecmd.delete_profile("mockprofile")
    assert mock_cliprofile_namespace.delete_profile.call_count == 0


def test_delete_all_profiles_does_nothing_if_user_doesnt_agree(
    user_disagreement, mock_cliprofile_namespace
):
    profilecmd.delete_all_profiles()
    assert mock_cliprofile_namespace.delete_profile.call_count == 0


def test_delete_all_deletes_all_existing_profiles(user_agreement, mock_cliprofile_namespace):
    mock_cliprofile_namespace.get_all_profiles.return_value = [
        create_mock_profile("test1"),
        create_mock_profile("test2"),
    ]
    profilecmd.delete_all_profiles()
    mock_cliprofile_namespace.delete_profile.assert_any_call("test1")
    mock_cliprofile_namespace.delete_profile.assert_any_call("test2")


def test_prompt_for_password_reset_if_credentials_valid_password_saved(
    mocker, user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_verify.return_value = True
    mock_cliprofile_namespace.profile_exists.return_value = False
    profilecmd.prompt_for_password_reset()
    mock_cliprofile_namespace.set_password.assert_called_once_with("newpassword", mocker.ANY)


def test_prompt_for_password_reset_if_credentials_invalid_password_not_saved(
    user_agreement, mock_verify, mock_cliprofile_namespace
):
    mock_verify.return_value = False
    mock_cliprofile_namespace.profile_exists.return_value = False
    success = False
    try:
        profilecmd.prompt_for_password_reset()
    except SystemExit:
        success = True
        assert not mock_cliprofile_namespace.set_password.call_count
    assert success


def test_list_profiles(caplog, mock_cliprofile_namespace):
    profiles = [
        create_mock_profile("one"),
        create_mock_profile("two"),
        create_mock_profile("three"),
    ]
    mock_cliprofile_namespace.get_all_profiles.return_value = profiles
    with caplog.at_level(logging.INFO):
        profilecmd.list_profiles()
        assert "one" in caplog.text
        assert "two" in caplog.text
        assert "three" in caplog.text


def test_list_profiles_when_no_profiles_outputs_no_profiles_message(
    caplog, mock_cliprofile_namespace
):
    mock_cliprofile_namespace.get_all_profiles.return_value = []
    profilecmd.list_profiles()
    with caplog.at_level(logging.ERROR):
        assert "No existing profile." in caplog.text


def test_use_profile(mock_cliprofile_namespace, profile):
    profilecmd.use_profile(profile)
    mock_cliprofile_namespace.switch_default_profile.assert_called_once_with(profile)
