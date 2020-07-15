import pytest

import code42cli.profile as cliprofile
from code42cli import PRODUCT_NAME
from code42cli.cmds.search.cursor_store import FileEventCursorStore, AlertCursorStore
from code42cli.config import ConfigAccessor, NoConfigProfileError
from .conftest import MockSection, create_mock_profile
from code42cli.errors import Code42CLIError


@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor, name="Config Accessor")
    attr = mocker.patch("{}.profile.config_accessor".format(PRODUCT_NAME), mock)
    return attr


@pytest.fixture
def password_setter(mocker):
    return mocker.patch("{}.password.set_password".format(PRODUCT_NAME))


@pytest.fixture
def password_getter(mocker):
    return mocker.patch("{}.password.get_stored_password".format(PRODUCT_NAME))


@pytest.fixture
def password_deleter(mocker):
    return mocker.patch("code42cli.password.delete_password")


class TestCode42Profile(object):
    def test_get_password_when_is_none_returns_password_from_getpass(self, mocker, password_getter):
        password_getter.return_value = None
        mock_getpass = mocker.patch("{}.password.get_password_from_prompt".format(PRODUCT_NAME))
        mock_getpass.return_value = "Test Password"
        actual = create_mock_profile().get_password()
        assert actual == "Test Password"

    def test_get_password_return_password_from_password_get_password(self, password_getter):
        password_getter.return_value = "Test Password"
        actual = create_mock_profile().get_password()
        assert actual == "Test Password"

    def test_authority_url_returns_expected_value(self):
        mock_profile = create_mock_profile()
        assert mock_profile.authority_url == "example.com"

    def test_name_returns_expected_value(self):
        mock_profile = create_mock_profile()
        assert mock_profile.name == "Test Profile Name"

    def test_username_returns_expected_value(self):
        mock_profile = create_mock_profile()
        assert mock_profile.username == "foo"

    def test_ignore_ssl_errors_returns_expected_value(self):
        mock_profile = create_mock_profile()
        assert mock_profile.ignore_ssl_errors == True


def test_get_profile_returns_expected_profile(config_accessor):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    profile = cliprofile.get_profile("testprofilename")
    assert profile.name == "testprofilename"


def test_get_profile_when_config_accessor_raises_cli_error(config_accessor):
    config_accessor.get_profile.side_effect = NoConfigProfileError()
    with pytest.raises(Code42CLIError):
        cliprofile.get_profile("testprofilename")


def test_default_profile_exists_when_exists_returns_true(config_accessor):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    assert cliprofile.default_profile_exists()


def test_default_profile_exists_when_not_exists_returns_false(config_accessor):
    mock_section = MockSection(ConfigAccessor.DEFAULT_VALUE)
    config_accessor.get_profile.return_value = mock_section
    assert not cliprofile.default_profile_exists()


def test_validate_default_profile_prints_set_default_help_when_no_valid_default_but_another_profile_exists(
    capsys, config_accessor
):
    config_accessor.get_profile.side_effect = NoConfigProfileError()
    config_accessor.get_all_profiles.return_value = [MockSection("thisprofilexists")]
    with pytest.raises(Code42CLIError):
        cliprofile.validate_default_profile()
        capture = capsys.readouterr()
        assert "No default profile set." in capture.out


def test_validate_default_profile_prints_create_profile_help_when_no_valid_default_and_no_other_profiles_exists(
    capsys, config_accessor
):
    config_accessor.get_profile.side_effect = NoConfigProfileError()
    config_accessor.get_all_profiles.return_value = []
    with pytest.raises(Code42CLIError):
        cliprofile.validate_default_profile()
        capture = capsys.readouterr()
        assert "No existing profile." in capture.out


def test_profile_exists_when_exists_returns_true(config_accessor):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    assert cliprofile.profile_exists("testprofilename")


def test_profile_exists_when_not_exists_returns_false(config_accessor):
    config_accessor.get_profile.side_effect = NoConfigProfileError()
    assert not cliprofile.profile_exists("idontexist")


def test_switch_default_profile_switches_to_expected_profile(config_accessor):
    mock_section = MockSection("switchtome")
    config_accessor.get_profile.return_value = mock_section
    cliprofile.switch_default_profile("switchtome")
    config_accessor.switch_default_profile.assert_called_once_with("switchtome")


def test_create_profile_uses_expected_profile_values(config_accessor):
    config_accessor.get_profile.side_effect = NoConfigProfileError()
    profile_name = "profilename"
    server = "server"
    username = "username"
    ssl_errors_disabled = True
    cliprofile.create_profile(profile_name, server, username, ssl_errors_disabled)
    config_accessor.create_profile.assert_called_once_with(
        profile_name, server, username, ssl_errors_disabled
    )


def test_create_profile_if_profile_exists_exits(mocker, cli_state, caplog, config_accessor):
    config_accessor.get_profile.return_value = mocker.MagicMock()
    with pytest.raises(Code42CLIError):
        cliprofile.create_profile("foo", "bar", "baz", True)


def test_get_all_profiles_returns_expected_profile_list(config_accessor):
    config_accessor.get_all_profiles.return_value = [
        create_mock_profile("one"),
        create_mock_profile("two"),
    ]
    profiles = cliprofile.get_all_profiles()
    assert len(profiles) == 2
    assert profiles[0].name == "one"
    assert profiles[1].name == "two"


def test_get_stored_password_returns_expected_password(config_accessor, password_getter):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    test_profile = "testprofilename"
    password_getter.return_value = "testpassword"
    assert cliprofile.get_stored_password("testprofilename") == "testpassword"


def test_get_stored_password_uses_expected_profile_name(config_accessor, password_getter):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    test_profile = "testprofilename"
    password_getter.return_value = "testpassword"
    cliprofile.get_stored_password(test_profile)
    assert password_getter.call_args[0][0].name == test_profile


def test_set_password_uses_expected_profile_name(config_accessor, password_setter):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    test_profile = "testprofilename"
    cliprofile.set_password("newpassword", test_profile)
    assert password_setter.call_args[0][0].name == test_profile


def test_set_password_uses_expected_password(config_accessor, password_setter):
    mock_section = MockSection("testprofilename")
    config_accessor.get_profile.return_value = mock_section
    test_profile = "testprofilename"
    cliprofile.set_password("newpassword", test_profile)
    assert password_setter.call_args[0][1] == "newpassword"


def test_delete_profile_deletes_password_if_exists(
    config_accessor, mocker, password_getter, password_deleter
):
    profile = create_mock_profile("deleteme")
    mock_get_profile = mocker.patch("code42cli.profile._get_profile")
    mock_get_profile.return_value = profile
    password_getter.return_value = "i_exist"
    cliprofile.delete_profile("deleteme")
    password_deleter.assert_called_once_with(profile)


def test_delete_profile_clears_checkpoints(config_accessor, mocker):
    profile = create_mock_profile("deleteme")
    mock_get_profile = mocker.patch("code42cli.profile._get_profile")
    mock_get_profile.return_value = profile
    event_store = mocker.MagicMock(spec=FileEventCursorStore)
    alert_store = mocker.MagicMock(spec=AlertCursorStore)
    mock_get_cursor_store = mocker.patch("code42cli.profile.get_all_cursor_stores_for_profile")
    mock_get_cursor_store.return_value = [event_store, alert_store]
    cliprofile.delete_profile("deleteme")
    assert event_store.clean.call_count == 1
    assert alert_store.clean.call_count == 1
