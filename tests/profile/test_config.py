from __future__ import with_statement

import pytest

import code42cli.profile.config as config

_DEFAULT_PROFILE_NAME = "Default Profile"


@pytest.fixture(autouse=True)
def reader(mocker):
    mocker.patch("configparser.ConfigParser.read")


@pytest.fixture
def default_profile_name(mocker):
    default_name = mocker.patch("code42cli.profile.config._get_default_profile_name")
    default_name.return_value = _DEFAULT_PROFILE_NAME


def test_get_profile_when_there_are_no_sections_causes_exit(mocker):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = []
    with pytest.raises(SystemExit):
        config.get_profile()


def test_get_profile_when_not_given_name_uses_default(mocker, default_profile_name):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = [_DEFAULT_PROFILE_NAME, config.ConfigurationKeys.INTERNAL_SECTION]
    mock_getter = mocker.patch("code42cli.profile.config._get_profile_from_parser")
    config.get_profile()
    assert mock_getter.call_args[0][1] == _DEFAULT_PROFILE_NAME


def test_get_profile_uses_given_name(mocker):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = ["profile 1"]
    mock_getter = mocker.patch("code42cli.profile.config._get_profile_from_parser")
    config.get_profile("profile 1")
    assert mock_getter.call_args[0][1] == "profile 1"


def test_get_all_profile_ignores_internal_section(mocker):
    profile_names = [_DEFAULT_PROFILE_NAME, "profile 1", "profile 2"]
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = profile_names + [config.ConfigurationKeys.INTERNAL_SECTION]
    mock_get_profile = mocker.patch("code42cli.profile.config.get_profile")
    config.get_all_profiles()
    assert mock_get_profile.call_count == 3


def test_get_all_profile_returns_profiles_for_each_section(mocker):
    profile_names = [_DEFAULT_PROFILE_NAME, "profile 1", "profile 2"]
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = profile_names + [config.ConfigurationKeys.INTERNAL_SECTION]
    mock_get_profile = mocker.patch("code42cli.profile.config.get_profile")
    config.get_all_profiles()
    assert mock_get_profile.call_args_list[0][0][0] == _DEFAULT_PROFILE_NAME
    assert mock_get_profile.call_args_list[1][0][0] == "profile 1"
    assert mock_get_profile.call_args_list[2][0][0] == "profile 2"


def test_write_username_uses_default_profile_name_when_not_provided(mocker, default_profile_name):
    mock_getter = mocker.patch("code42cli.profile.config._get_profile_from_parser")
    mocker.patch("code42cli.profile.config._try_mark_setup_as_complete")
    config.write_username("test")
    assert mock_getter.call_args[0][1] == _DEFAULT_PROFILE_NAME


def test_write_authority_url_uses_default_profile_name_when_not_provided(
    mocker, default_profile_name
):
    mock_getter = mocker.patch("code42cli.profile.config._get_profile_from_parser")
    mocker.patch("code42cli.profile.config._try_mark_setup_as_complete")
    config.write_authority_url("test")
    assert mock_getter.call_args[0][1] == _DEFAULT_PROFILE_NAME


def test_write_ignore_ssl_errors_uses_default_profile_name_when_not_provided(
    mocker, default_profile_name
):
    mock_getter = mocker.patch("code42cli.profile.config._get_profile_from_parser")
    mocker.patch("code42cli.profile.config._try_mark_setup_as_complete")
    config.write_ignore_ssl_errors(True)
    assert mock_getter.call_args[0][1] == _DEFAULT_PROFILE_NAME
