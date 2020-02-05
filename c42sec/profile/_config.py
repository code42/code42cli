import os
from configparser import ConfigParser
from c42sec.util import get_user_project_path, print_error, print_bold


class ConfigurationKeys(object):
    USER_SECTION = u"Code42"
    AUTHORITY_KEY = u"c42_authority_url"
    USERNAME_KEY = u"c42_username"
    IGNORE_SSL_ERRORS_KEY = u"ignore-ssl-errors"
    INTERNAL_SECTION = u"Internal"
    HAS_SET_PROFILE_KEY = u"has_set_profile"


def get_config_profile():
    parser = ConfigParser()
    if not profile_has_been_set():
        print_error("ERROR: Profile is not set.")
        print("")
        print("To set, use: ")
        print_bold("\tc42sec profile set -s <authority-URL> -u <username>")
        print("")
        exit(1)

    return _get_config_profile_from_parser(parser)


def mark_as_set():
    parser = ConfigParser()
    config_file_path = get_config_file_path()
    parser.read(config_file_path)
    settings = parser[ConfigurationKeys.INTERNAL_SECTION]
    settings[ConfigurationKeys.HAS_SET_PROFILE_KEY] = "True"
    _save(parser)


def profile_has_been_set():
    parser = ConfigParser()
    config_file_path = get_config_file_path()
    parser.read(config_file_path)
    settings = parser[ConfigurationKeys.INTERNAL_SECTION]
    is_set = settings.getboolean(ConfigurationKeys.HAS_SET_PROFILE_KEY)
    return is_set


def set_username(new_username):
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)
    profile[ConfigurationKeys.USERNAME_KEY] = new_username
    _save(parser)


def set_authority_url(new_url):
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)
    profile[ConfigurationKeys.AUTHORITY_KEY] = new_url
    _save(parser)


def set_ignore_ssl_errors(new_value):
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)
    profile[ConfigurationKeys.IGNORE_SSL_ERRORS_KEY] = str(new_value)
    _save(parser)


def get_config_file_path():
    path = "{}/config.cfg".format(get_user_project_path())
    if not os.path.exists(path):
        _create_new_config_file(path)

    return path


def _get_config_profile_from_parser(parser):
    config_file_path = get_config_file_path()
    parser.read(config_file_path)
    config = parser[ConfigurationKeys.USER_SECTION]
    config.ignore_ssl_errors = config.getboolean(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)
    return config


def _create_new_config_file(path):
    config_parser = ConfigParser()
    config_parser = _create_user_section(config_parser)
    config_parser = _create_internal_section(config_parser)
    _save(config_parser, path)


def _create_user_section(parser):
    keys = ConfigurationKeys
    parser.add_section(keys.USER_SECTION)
    parser[keys.USER_SECTION] = {}
    parser[keys.USER_SECTION][keys.AUTHORITY_KEY] = "null"
    parser[keys.USER_SECTION][keys.USERNAME_KEY] = "null"
    parser[keys.USER_SECTION][keys.IGNORE_SSL_ERRORS_KEY] = "False"
    return parser


def _create_internal_section(parser):
    keys = ConfigurationKeys
    parser.add_section(keys.INTERNAL_SECTION)
    parser[keys.INTERNAL_SECTION] = {}
    parser[keys.INTERNAL_SECTION][keys.HAS_SET_PROFILE_KEY] = "False"
    return parser


def _save(parser, path=None):
    path = get_config_file_path() if path is None else path
    with open(path, "w+") as config_file:
        parser.write(config_file)
