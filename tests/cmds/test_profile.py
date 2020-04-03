import pytest

import code42cli.cmds.profile as profilecmd
from ..conftest import create_mock_profile


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
def mock_cliprofile_ns(mocker):
    return mocker.patch("code42cli.cmds.profile.cliprofile")


@pytest.fixture(autouse=True)
def mock_getpass(mocker):
    mock = mocker.patch("code42cli.cmds.profile.getpass")
    mock.return_value = "newpassword"


@pytest.fixture
def mock_verify(mocker):
    return mocker.patch("code42cli.cmds.profile.validate_connection")


def test_show_profile_outputs_profile_info(capsys, mock_cliprofile_ns, profile):
    profile.name = "testname"
    profile.authority_url = "example.com"
    profile.username = "foo"
    profile.disable_ssl_errors = True
    mock_cliprofile_ns.get_profile.return_value = profile
    profilecmd.show_profile(profile)
    capture = capsys.readouterr()
    assert "testname" in capture.out
    assert "example.com" in capture.out
    assert "foo" in capture.out
    assert "A password is set" in capture.out


def test_show_profile_when_password_set_outputs_password_note(capsys, mock_cliprofile_ns, profile):
    mock_cliprofile_ns.get_profile.return_value = profile
    mock_cliprofile_ns.get_stored_password.return_value = None
    profilecmd.show_profile(profile)
    capture = capsys.readouterr()
    assert "A password is set" not in capture.out


def test_create_profile_if_profile_exists_exits(capsys, mock_cliprofile_ns):
    mock_cliprofile_ns.profile_exists.return_value = True
    with pytest.raises(SystemExit):
        profilecmd.create_profile("foo", "bar", "baz", True)
    capture = capsys.readouterr()
    assert "already exists" in capture.out


def test_create_profile_if_user_sets_password_is_created(
    user_agreement, mock_verify, mock_cliprofile_ns
):
    mock_cliprofile_ns.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    mock_cliprofile_ns.create_or_update_profile.assert_called_once_with("foo", "bar", "baz", True)


def test_create_profile_if_user_does_not_set_password_is_created(
    user_disagreement, mock_verify, mock_cliprofile_ns
):
    mock_cliprofile_ns.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    mock_cliprofile_ns.create_or_update_profile.assert_called_once_with("foo", "bar", "baz", True)


def test_create_profile_if_credentials_invalid_password_not_saved(
    user_agreement, mock_verify, mock_cliprofile_ns
):
    mock_verify.return_value = False
    mock_cliprofile_ns.profile_exists.return_value = False
    with pytest.raises(SystemExit):
        profilecmd.create_profile("foo", "bar", "baz", True)
    assert not mock_cliprofile_ns.set_password.call_count


def test_create_profile_if_credentials_valid_password_saved(
    mocker, user_agreement, mock_verify, mock_cliprofile_ns
):
    mock_verify.return_value = True
    mock_cliprofile_ns.profile_exists.return_value = False
    profilecmd.create_profile("foo", "bar", "baz", True)
    mock_cliprofile_ns.set_password.assert_called_once_with("newpassword", mocker.ANY)


def test_prompt_for_password_reset_if_credentials_valid_password_saved(
    mocker, user_agreement, mock_verify, mock_cliprofile_ns
):
    mock_verify.return_value = True
    mock_cliprofile_ns.profile_exists.return_value = False
    profilecmd.prompt_for_password_reset()
    mock_cliprofile_ns.set_password.assert_called_once_with("newpassword", mocker.ANY)


def test_prompt_for_password_reset_if_credentials_invalid_password_not_saved(
    user_agreement, mock_verify, mock_cliprofile_ns
):
    mock_verify.return_value = False
    mock_cliprofile_ns.profile_exists.return_value = False
    with pytest.raises(SystemExit):
        profilecmd.prompt_for_password_reset()
    assert not mock_cliprofile_ns.set_password.call_count


def test_list_profiles(capsys, mock_cliprofile_ns):
    profiles = [
        create_mock_profile("one"),
        create_mock_profile("two"),
        create_mock_profile("three"),
    ]
    mock_cliprofile_ns.get_all_profiles.return_value = profiles
    profilecmd.list_profiles()
    capture = capsys.readouterr()
    assert "one" in capture.out
    assert "two" in capture.out
    assert "three" in capture.out


def test_list_profiles_when_no_profiles_outputs_no_profiles_message(capsys, mock_cliprofile_ns):
    mock_cliprofile_ns.get_all_profiles.return_value = []
    profilecmd.list_profiles()
    capture = capsys.readouterr()
    assert "No existing profile." in capture.out


def test_use_profile(mock_cliprofile_ns, profile):
    profilecmd.use_profile(profile)
    mock_cliprofile_ns.switch_default_profile.assert_called_once_with(profile)
