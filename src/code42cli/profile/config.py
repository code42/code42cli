from __future__ import print_function

import os
from configparser import ConfigParser

import code42cli.util as util
from code42cli.compat import str

DEFAULT_VALUE = u"__DEFAULT__"
_PROFILE_ENV_VAR_NAME = u"CODE42CLI_PROFILE"


class ConfigurationKeys(object):
    AUTHORITY_KEY = u"c42_authority_url"
    USERNAME_KEY = u"c42_username"
    IGNORE_SSL_ERRORS_KEY = u"ignore-ssl-errors"
    INTERNAL_SECTION = u"Internal"
    HAS_SET_PROFILE_KEY = u"default_profile_is_complete"
    DEFAULT_PROFILE = u"default_profile"


def get_config_profile(profile_name=None):
    """Gets the config file variables for the given name.

        Args:
            profile_name: The name of the profile to get variables for.
            If None, uses the default profile name.
    """
    parser = ConfigParser()
    available_profiles = get_all_profile_names()
    if len(available_profiles) == 0:
        util.print_no_existing_profile_message()
        exit(1)

    if profile_name and profile_name not in available_profiles:
        _print_profile_not_exists_message(profile_name)
        exit(1)

    if not profile_name:
        profile_name = get_default_profile_name()

    return _get_profile_from_parser(parser, profile_name)


def get_default_profile_name():
    parser = ConfigParser()
    _attach_config_file_to_profile(parser)
    return parser[ConfigurationKeys.INTERNAL_SECTION][ConfigurationKeys.DEFAULT_PROFILE]


def get_all_profile_names():
    parser = ConfigParser()
    _attach_config_file_to_profile(parser)
    sections = list(parser.sections())
    if ConfigurationKeys.INTERNAL_SECTION in sections:
        sections.remove(ConfigurationKeys.INTERNAL_SECTION)
    return sections


def set_username(new_username, profile_name=None):
    profile_name = profile_name or get_default_profile_name()
    parser = ConfigParser()
    profile = _get_profile_from_parser(parser, profile_name)
    profile[ConfigurationKeys.USERNAME_KEY] = new_username
    _save(parser, profile_name, ConfigurationKeys.USERNAME_KEY)
    _try_mark_setup_as_complete(profile_name)


def set_authority_url(new_url, profile_name=None):
    profile_name = profile_name or get_default_profile_name()
    parser = ConfigParser()
    profile = _get_profile_from_parser(parser, profile_name)
    profile[ConfigurationKeys.AUTHORITY_KEY] = new_url
    _save(parser, profile_name, ConfigurationKeys.AUTHORITY_KEY)
    _try_mark_setup_as_complete(profile_name)


def set_ignore_ssl_errors(new_value, profile_name=None):
    profile_name = profile_name or get_default_profile_name()
    parser = ConfigParser()
    profile = _get_profile_from_parser(parser, profile_name)
    profile[ConfigurationKeys.IGNORE_SSL_ERRORS_KEY] = str(new_value)
    _save(parser, profile_name, ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)


def _try_mark_setup_as_complete(profile_name):
    profile_name = profile_name or get_default_profile_name()
    if not _setup_ready_for_completion(profile_name):
        return
    parser = ConfigParser()
    config_file_path = _get_config_file_path(profile_name)
    parser.read(config_file_path)
    settings = parser[ConfigurationKeys.INTERNAL_SECTION]
    settings[ConfigurationKeys.HAS_SET_PROFILE_KEY] = str(True)
    _save(parser, profile_name, ConfigurationKeys.HAS_SET_PROFILE_KEY)


def _setup_ready_for_completion(profile_name):
    parser = ConfigParser()
    profile = _get_profile_from_parser(parser, profile_name)
    username = profile[ConfigurationKeys.USERNAME_KEY]
    authority = profile[ConfigurationKeys.AUTHORITY_KEY]
    username_exists = username is not None and username != DEFAULT_VALUE
    authority_exists = authority is not None and authority != DEFAULT_VALUE
    return username_exists and authority_exists and not _profile_has_been_set()


def _profile_has_been_set():
    parser = ConfigParser()
    config_file_path = _get_config_file_path()
    parser.read(config_file_path)
    settings = parser[ConfigurationKeys.INTERNAL_SECTION]
    return settings.getboolean(ConfigurationKeys.HAS_SET_PROFILE_KEY)


def _get_profile_from_parser(parser, profile_name):
    _attach_config_file_to_profile(parser, profile_name)
    if profile_name not in parser.sections():
        _create_profile_section(parser, profile_name)
    return parser[profile_name]


def _attach_config_file_to_profile(parser, profile_name=None):
    config_file_path = _get_config_file_path(profile_name)
    parser.read(config_file_path)


def _save(parser, profile_name, key=None, path=None):
    path = _get_config_file_path(profile_name) if path is None else path
    util.open_file(path, u"w+", lambda f: parser.write(f))
    if key is not None:
        if key == ConfigurationKeys.HAS_SET_PROFILE_KEY:
            print(u"You have completed setting up your profile!")
        else:
            print(u"'{}' has been successfully updated".format(key))


def _get_config_file_path(profile_name=None):
    path = u"{}config.cfg".format(util.get_user_project_path())
    if not os.path.exists(path):
        _create_new_config_file(path, profile_name)
    return path


def _create_new_config_file(path, profile_name):
    profile_name = profile_name or DEFAULT_VALUE
    config_parser = ConfigParser()
    config_parser = _create_internal_section(config_parser)
    if profile_name != DEFAULT_VALUE:
        config_parser = _create_profile_section(config_parser, profile_name)
    _save(config_parser, profile_name, None, path)


def _create_internal_section(parser):
    keys = ConfigurationKeys
    parser.add_section(keys.INTERNAL_SECTION)
    parser[keys.INTERNAL_SECTION] = {}
    parser[keys.INTERNAL_SECTION][keys.HAS_SET_PROFILE_KEY] = str(False)
    parser[keys.INTERNAL_SECTION][keys.DEFAULT_PROFILE] = DEFAULT_VALUE
    return parser


def _create_profile_section(parser, profile_name):
    keys = ConfigurationKeys
    parser.add_section(profile_name)
    parser[profile_name] = {}
    parser[profile_name][keys.AUTHORITY_KEY] = DEFAULT_VALUE
    parser[profile_name][keys.USERNAME_KEY] = DEFAULT_VALUE
    parser[profile_name][keys.IGNORE_SSL_ERRORS_KEY] = str(False)

    default_profile = parser[keys.INTERNAL_SECTION].get(keys.DEFAULT_PROFILE)
    if default_profile is None or default_profile is DEFAULT_VALUE:
        parser[keys.INTERNAL_SECTION][keys.DEFAULT_PROFILE] = profile_name
    return parser


def _print_profile_not_exists_message(profile_name):
    util.print_error(u"Profile '{0}' does not exist.".format(profile_name))
    util.print_set_profile_help()
