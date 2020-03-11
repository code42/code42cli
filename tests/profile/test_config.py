from __future__ import with_statement
import pytest
from configparser import ConfigParser

from code42cli.profile.config import ConfigAccessor


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.MagicMock(sepc=ConfigParser)


@pytest.fixture
def mock_saver(mocker):
    return mocker.patch("code42cli.util.open_file")


def create_mock_profile_object(name, authority=None, username=None):
    authority = authority or ConfigAccessor.DEFAULT_VALUE
    username = username or ConfigAccessor.DEFAULT_VALUE
    profile_dict = {ConfigAccessor.AUTHORITY_KEY: authority, ConfigAccessor.USERNAME_KEY: username}

    class ProfileObject(object):
        def __getitem__(self, item):
            return profile_dict[item]

        def __setitem__(self, key, value):
            profile_dict[key] = value

        def get(self, item):
            return profile_dict.get(item)

        @property
        def name(self):
            return name

    return ProfileObject()


def create_internal_object(is_complete, default_profile_name=None):
    default_profile_name = default_profile_name or ConfigAccessor.DEFAULT_VALUE
    internal_dict = {
        ConfigAccessor.DEFAULT_PROFILE: default_profile_name,
        ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE: is_complete,
    }

    class InternalObject(object):
        def __getitem__(self, item):
            return internal_dict[item]

        def __setitem__(self, key, value):
            internal_dict[key] = value

        def getboolean(self, *args):
            return is_complete

    return InternalObject()


def setup_parser_one_profile(profile, internal, parser):
    def side_effect(item):
        if item == "ProfileA":
            return profile
        elif item == "Internal":
            return internal

    parser.__getitem__.side_effect = side_effect


class TestConfigAccessor(object):
    def test_get_profile_when_profile_does_not_exist_raises(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal"]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(Exception):
            accessor.get_profile("Profile Name that does not exist")

    def test_get_profile_when_profile_has_default_name_raises(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal"]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(Exception):
            accessor.get_profile("__DEFAULT__")

    def test_get_profile_returns_expected_profile(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        accessor.get_profile("ProfileA")
        assert mock_config_parser.__getitem__.call_args[0][0] == "ProfileA"

    def test_get_all_profiles_excludes_internal_section(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["ProfileA", "Internal", "ProfileB"]
        accessor = ConfigAccessor(mock_config_parser)
        profiles = accessor.get_all_profiles()
        for p in profiles:
            if p.name == "Internal":
                assert False

    def test_set_username_marks_as_complete_if_ready(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile = create_mock_profile_object("ProfileA", "example.com", None)
        mock_internal = create_internal_object(False)
        setup_parser_one_profile(mock_profile, mock_internal, mock_config_parser)
        accessor.set_username("TestUser", "ProfileA")
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE] == "ProfileA"
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE]

    def test_set_username_does_not_mark_as_complete_if_not_have_authority(
        self, mock_config_parser, mock_saver
    ):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile = create_mock_profile_object("ProfileA", None, None)
        mock_internal = create_internal_object(False)
        setup_parser_one_profile(mock_profile, mock_internal, mock_config_parser)
        accessor.set_username("TestUser", "ProfileA")
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE] == ConfigAccessor.DEFAULT_VALUE
        assert not mock_internal[ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE]

    def test_set_username_saves(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile = create_mock_profile_object("ProfileA", "example.com", "console.com")
        mock_internal = create_internal_object(True, "ProfileA")
        setup_parser_one_profile(mock_profile, mock_internal, mock_config_parser)
        accessor.set_username("TestUser", "ProfileA")
        assert mock_saver.call_count

    def test_set_authority_marks_as_complete_if_ready(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile = create_mock_profile_object("ProfileA", None, "test.testerson")
        mock_internal = create_internal_object(False)
        setup_parser_one_profile(mock_profile, mock_internal, mock_config_parser)
        accessor.set_authority_url("new url", "ProfileA")
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE] == "ProfileA"
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE]

    def test_set_authority_does_not_mark_as_complete_if_not_have_username(
        self, mock_config_parser, mock_saver
    ):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile = create_mock_profile_object("ProfileA", None, None)
        mock_internal = create_internal_object(False)
        setup_parser_one_profile(mock_profile, mock_internal, mock_config_parser)
        accessor.set_authority_url("new url", "ProfileA")
        assert mock_internal[ConfigAccessor.DEFAULT_PROFILE] == ConfigAccessor.DEFAULT_VALUE
        assert not mock_internal[ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE]

    def test_set_authority_saves(self, mock_config_parser, mock_saver):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        mock_profile = create_mock_profile_object("ProfileA", None, None)
        mock_internal = create_internal_object(True, "ProfileA")
        setup_parser_one_profile(mock_profile, mock_internal, mock_config_parser)
        accessor.set_authority_url("new url", "ProfileA")
        assert mock_saver.call_count == 1

    def test_switch_default_profile_switches_internal_value(self, mock_config_parser, mock_saver):
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
        assert mock_saver.call_count == 1

    def test_create_profile_if_not_exists_when_given_default_name_does_not_create(
        self, mock_config_parser, mock_saver
    ):
        mock_config_parser.sections.return_value = ["Internal", "ProfileA"]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(Exception):
            accessor.create_profile_if_not_exists(ConfigAccessor.DEFAULT_VALUE)
