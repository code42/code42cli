from __future__ import with_statement

from configparser import ConfigParser

import pytest

from code42cli.config import ConfigAccessor
from .conftest import MockSection


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.MagicMock(sepc=ConfigParser)


@pytest.fixture(autouse=True)
def mock_saver(mocker):
    return mocker.patch("code42cli.util.open_file")


def create_mock_profile_object(profile_name, authority_url=None, username=None):
    mock_profile = MockSection(profile_name)
    mock_profile[ConfigAccessor.AUTHORITY_KEY] = authority_url
    mock_profile[ConfigAccessor.USERNAME_KEY] = username
    return mock_profile


def create_internal_object(is_complete, default_profile_name=None):
    default_profile_name = default_profile_name or ConfigAccessor.DEFAULT_VALUE
    internal_dict = {
        ConfigAccessor.DEFAULT_PROFILE: default_profile_name,
        ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE: is_complete,
    }
    internal_section = MockSection("Internal", internal_dict)

    def getboolean(*args):
        return is_complete

    internal_section.getboolean = getboolean
    return internal_section


def setup_parser_one_profile(profile, internal, parser):
    def side_effect(item):
        if item == "ProfileA":
            return profile
        elif item == "Internal":
            return internal

    parser.__getitem__.side_effect = side_effect


class TestConfigAccessor(object):
    def test_get_profile_when_profile_does_not_exist_raises(self, mock_config_parser):
        mock_config_parser.sections.return_value = ["Internal"]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(Exception):
            accessor.get_profile("Profile Name that does not exist")

    def test_get_profile_when_profile_has_default_name_raises(self, mock_config_parser):
        mock_config_parser.sections.return_value = ["Internal"]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(Exception):
            accessor.get_profile("__DEFAULT__")

    def test_get_profile_returns_expected_profile(self, mock_config_parser):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        accessor.get_profile("ProfileA")
        assert mock_config_parser.__getitem__.call_args[0][0] == "ProfileA"

    def test_get_all_profiles_excludes_internal_section(self, mock_config_parser):
        mock_config_parser.sections.return_value = ["ProfileA", "Internal", "ProfileB"]
        accessor = ConfigAccessor(mock_config_parser)
        profiles = accessor.get_all_profiles()
        for p in profiles:
            if p.name == "Internal":
                assert False

    def test_get_all_profiles_returns_profiles_with_expected_values(self, mock_config_parser):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA", "ProfileB"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile_a = create_mock_profile_object("ProfileA", "test", "test")
        mock_profile_b = create_mock_profile_object("ProfileB", "test", "test")

        mock_internal = create_internal_object(True, "ProfileA")

        def side_effect(item):
            if item == "ProfileA":
                return mock_profile_a
            elif item == "ProfileB":
                return mock_profile_b
            elif item == "Internal":
                return mock_internal

        mock_config_parser.__getitem__.side_effect = side_effect
        profiles = accessor.get_all_profiles()
        assert profiles[0].name == "ProfileA"
        assert profiles[1].name == "ProfileB"

    def test_switch_default_profile_switches_internal_value(self, mock_config_parser):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA", "ProfileB"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile_a = create_mock_profile_object("ProfileA", "test", "test")
        mock_profile_b = create_mock_profile_object("ProfileB", "test", "test")

        mock_internal = create_internal_object(True, "ProfileA")

        def side_effect(item):
            if item == "ProfileA":
                return mock_profile_a
            elif item == "ProfileB":
                return mock_profile_b
            elif item == "Internal":
                return mock_internal

        mock_config_parser.__getitem__.side_effect = side_effect
        accessor.switch_default_profile("ProfileB")
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE] == "ProfileB"

    def test_switch_default_profile_saves(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA", "ProfileB"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile_a = create_mock_profile_object("ProfileA", "test", "test")
        mock_profile_b = create_mock_profile_object("ProfileB", "test", "test")

        mock_internal = create_internal_object(True, "ProfileA")

        def side_effect(item):
            if item == "ProfileA":
                return mock_profile_a
            elif item == "ProfileB":
                return mock_profile_b
            elif item == "Internal":
                return mock_internal

        mock_config_parser.__getitem__.side_effect = side_effect
        accessor.switch_default_profile("ProfileB")
        assert mock_saver.call_count

    def test_create_or_update_profile_when_given_default_name_does_not_create(
        self, mock_config_parser
    ):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(Exception):
            accessor.create_or_update_profile(ConfigAccessor.DEFAULT_VALUE, "foo", "bar", False)

    def test_create_or_update_profile_when_not_existing_saves(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal"]
        mock_profile = create_mock_profile_object("ProfileA", None, None)
        mock_internal = create_internal_object(False)
        mock_internal["default_profile_is_complete"] = "False"
        setup_parser_one_profile(mock_internal, mock_internal, mock_config_parser)
        accessor = ConfigAccessor(mock_config_parser)

        accessor.create_or_update_profile("ProfileA", "example.com", "bar", False)
        assert mock_saver.call_count
