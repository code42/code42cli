from configparser import ConfigParser

import pytest

from .conftest import MockSection
from code42cli.config import ConfigAccessor
from code42cli.config import NoConfigProfileError

_TEST_PROFILE_NAME = "ProfileA"
_TEST_SECOND_PROFILE_NAME = "ProfileB"
_INTERNAL = "Internal"


@pytest.fixture(autouse=True)
def mock_saver(mocker):
    return mocker.patch("code42cli.config.open")


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.MagicMock(sepc=ConfigParser)


@pytest.fixture
def config_parser_for_multiple_profiles(mock_config_parser):
    mock_config_parser.sections.return_value = [
        _INTERNAL,
        _TEST_PROFILE_NAME,
        _TEST_SECOND_PROFILE_NAME,
    ]
    mock_profile_a = create_mock_profile_object(_TEST_PROFILE_NAME, "test", "test")
    mock_profile_b = create_mock_profile_object(
        _TEST_SECOND_PROFILE_NAME, "test", "test"
    )

    mock_internal = create_internal_object(True, _TEST_PROFILE_NAME)

    def side_effect(item):
        if item == _TEST_PROFILE_NAME:
            return mock_profile_a
        elif item == _TEST_SECOND_PROFILE_NAME:
            return mock_profile_b
        elif item == _INTERNAL:
            return mock_internal

    mock_config_parser.__getitem__.side_effect = side_effect
    return mock_config_parser


@pytest.fixture
def config_parser_for_create(mock_config_parser):
    values = [[_INTERNAL], [_INTERNAL, _TEST_PROFILE_NAME]]

    def side_effect():
        if len(values) == 2:
            return values.pop(0)
        return values[0]

    mock_config_parser.sections.side_effect = side_effect
    return mock_config_parser


def create_mock_profile_object(profile_name, authority_url=None, username=None):
    mock_profile = MockSection(profile_name)
    mock_profile[ConfigAccessor.AUTHORITY_KEY] = authority_url
    mock_profile[ConfigAccessor.USERNAME_KEY] = username
    return mock_profile


def create_internal_object(is_complete, default_profile_name=None):
    default_profile_name = default_profile_name or ConfigAccessor.DEFAULT_VALUE
    internal_dict = {ConfigAccessor.DEFAULT_PROFILE: default_profile_name}
    internal_section = MockSection(_INTERNAL, internal_dict)

    def getboolean(*args):
        return is_complete

    internal_section.getboolean = getboolean
    return internal_section


def setup_parser_one_profile(profile, internal, parser):
    def side_effect(item):
        if item == _TEST_PROFILE_NAME:
            return profile
        elif item == _INTERNAL:
            return internal

    parser.__getitem__.side_effect = side_effect


class TestConfigAccessor:
    def test_get_profile_when_profile_does_not_exist_raises(self, mock_config_parser):
        mock_config_parser.sections.return_value = [_INTERNAL]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(NoConfigProfileError):
            accessor.get_profile("Profile Name that does not exist")

    def test_get_profile_when_profile_has_default_name_raises(self, mock_config_parser):
        mock_config_parser.sections.return_value = [_INTERNAL]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(NoConfigProfileError):
            accessor.get_profile(ConfigAccessor.DEFAULT_VALUE)

    def test_get_profile_returns_expected_profile(self, mock_config_parser):
        mock_config_parser.sections.return_value = [_INTERNAL, _TEST_PROFILE_NAME]
        accessor = ConfigAccessor(mock_config_parser)
        accessor.get_profile(_TEST_PROFILE_NAME)
        assert mock_config_parser.__getitem__.call_args[0][0] == _TEST_PROFILE_NAME

    def test_get_all_profiles_excludes_internal_section(self, mock_config_parser):
        mock_config_parser.sections.return_value = [
            _TEST_PROFILE_NAME,
            _INTERNAL,
            _TEST_SECOND_PROFILE_NAME,
        ]
        accessor = ConfigAccessor(mock_config_parser)
        profiles = accessor.get_all_profiles()
        for p in profiles:
            if p.name == _INTERNAL:
                raise AssertionError()

    def test_get_all_profiles_returns_profiles_with_expected_values(
        self, config_parser_for_multiple_profiles
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_profiles)
        profiles = accessor.get_all_profiles()
        assert profiles[0].name == _TEST_PROFILE_NAME
        assert profiles[1].name == _TEST_SECOND_PROFILE_NAME

    def test_switch_default_profile_switches_internal_value(
        self, config_parser_for_multiple_profiles
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_profiles)
        accessor.switch_default_profile(_TEST_SECOND_PROFILE_NAME)
        assert (
            config_parser_for_multiple_profiles[_INTERNAL][
                ConfigAccessor.DEFAULT_PROFILE
            ]
            == _TEST_SECOND_PROFILE_NAME
        )

    def test_switch_default_profile_saves(
        self, config_parser_for_multiple_profiles, mock_saver
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_profiles)
        accessor.switch_default_profile(_TEST_SECOND_PROFILE_NAME)
        assert mock_saver.call_count

    def test_create_profile_when_given_default_name_does_not_create(
        self, config_parser_for_create
    ):
        accessor = ConfigAccessor(config_parser_for_create)
        with pytest.raises(Exception):
            accessor.create_profile(ConfigAccessor.DEFAULT_VALUE, "foo", "bar", False)

    def test_create_profile_when_no_default_profile_sets_default(
        self, mocker, config_parser_for_create, mock_saver
    ):
        create_mock_profile_object(_TEST_PROFILE_NAME, None, None)
        mock_internal = create_internal_object(False)
        setup_parser_one_profile(mock_internal, mock_internal, config_parser_for_create)
        accessor = ConfigAccessor(config_parser_for_create)
        accessor.switch_default_profile = mocker.MagicMock()

        accessor.create_profile(_TEST_PROFILE_NAME, "example.com", "bar", False)
        assert accessor.switch_default_profile.call_count == 1

    def test_create_profile_when_has_default_profile_does_not_set_default(
        self, mocker, config_parser_for_create, mock_saver
    ):
        create_mock_profile_object(_TEST_PROFILE_NAME, None, None)
        mock_internal = create_internal_object(True, _TEST_PROFILE_NAME)
        setup_parser_one_profile(mock_internal, mock_internal, config_parser_for_create)
        accessor = ConfigAccessor(config_parser_for_create)
        accessor.switch_default_profile = mocker.MagicMock()

        accessor.create_profile(_TEST_PROFILE_NAME, "example.com", "bar", False)
        assert not accessor.switch_default_profile.call_count

    def test_create_profile_when_not_existing_saves(
        self, config_parser_for_create, mock_saver
    ):
        create_mock_profile_object(_TEST_PROFILE_NAME, None, None)
        mock_internal = create_internal_object(False)
        setup_parser_one_profile(mock_internal, mock_internal, config_parser_for_create)
        accessor = ConfigAccessor(config_parser_for_create)

        accessor.create_profile(_TEST_PROFILE_NAME, "example.com", "bar", False)
        assert mock_saver.call_count

    def test_update_profile_when_no_profile_exists_raises_exception(
        self, config_parser_for_multiple_profiles
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_profiles)
        with pytest.raises(Exception):
            accessor.update_profile("Non-existent Profile")

    def test_update_profile_updates_profile(self, config_parser_for_multiple_profiles):
        accessor = ConfigAccessor(config_parser_for_multiple_profiles)
        address = "NEW ADDRESS"
        username = "NEW USERNAME"

        accessor.update_profile(_TEST_PROFILE_NAME, address, username, True)
        assert (
            accessor.get_profile(_TEST_PROFILE_NAME)[ConfigAccessor.AUTHORITY_KEY]
            == address
        )
        assert (
            accessor.get_profile(_TEST_PROFILE_NAME)[ConfigAccessor.USERNAME_KEY]
            == username
        )
        assert accessor.get_profile(_TEST_PROFILE_NAME)[
            ConfigAccessor.IGNORE_SSL_ERRORS_KEY
        ]

    def test_update_profile_does_not_update_when_given_none(
        self, config_parser_for_multiple_profiles
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_profiles)

        # First, make sure they're not None
        address = "NOT NONE"
        username = "NOT NONE"
        accessor.update_profile(_TEST_PROFILE_NAME, address, username, True)

        accessor.update_profile(_TEST_PROFILE_NAME, None, None, None)
        assert (
            accessor.get_profile(_TEST_PROFILE_NAME)[ConfigAccessor.AUTHORITY_KEY]
            == address
        )
        assert (
            accessor.get_profile(_TEST_PROFILE_NAME)[ConfigAccessor.USERNAME_KEY]
            == username
        )
        assert accessor.get_profile(_TEST_PROFILE_NAME)[
            ConfigAccessor.IGNORE_SSL_ERRORS_KEY
        ]
