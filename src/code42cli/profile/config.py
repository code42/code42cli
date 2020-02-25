from __future__ import print_function
import os
from configparser import ConfigParser

from code42cli.compat import str
import code42cli.util as util


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
        util.print_error("Profile is not set.")
        print("")
        print("To set, use: ")
        util.print_bold("\tcode42cli profile set -s <authority-URL> -u <username>")
        print("")
        exit(1)

    return _get_config_profile_from_parser(parser)


def mark_as_set():
    parser = ConfigParser()
    config_file_path = _get_config_file_path()
    parser.read(config_file_path)
    settings = parser[ConfigurationKeys.INTERNAL_SECTION]
    settings[ConfigurationKeys.HAS_SET_PROFILE_KEY] = "True"
    _save(parser, ConfigurationKeys.HAS_SET_PROFILE_KEY)


def profile_has_been_set():
    parser = ConfigParser()
    config_file_path = _get_config_file_path()
    parser.read(config_file_path)
    settings = parser[ConfigurationKeys.INTERNAL_SECTION]
    return settings.getboolean(ConfigurationKeys.HAS_SET_PROFILE_KEY)


def set_username(new_username):
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)
    profile[ConfigurationKeys.USERNAME_KEY] = new_username
    _save(parser, ConfigurationKeys.USERNAME_KEY)


def set_authority_url(new_url):
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)
    profile[ConfigurationKeys.AUTHORITY_KEY] = new_url
    _save(parser, ConfigurationKeys.AUTHORITY_KEY)


def set_ignore_ssl_errors(new_value):
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)
    profile[ConfigurationKeys.IGNORE_SSL_ERRORS_KEY] = str(new_value)
    _save(parser, ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)


def _get_config_file_path():
    path = "{}config.cfg".format(util.get_user_project_path())
    if not os.path.exists(path) or not _verify_config_file(path):
        _create_new_config_file(path)

    return path


def _get_config_profile_from_parser(parser):
    config_file_path = _get_config_file_path()
    parser.read(config_file_path)
    config = parser[ConfigurationKeys.USER_SECTION]
    config.ignore_ssl_errors = config.getboolean(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)
    return config


def _create_new_config_file(path):
    config_parser = ConfigParser()
    config_parser = _create_user_section(config_parser)
    config_parser = _create_internal_section(config_parser)
    _save(config_parser, None, path)


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


def _save(parser, key=None, path=None):
    path = _get_config_file_path() if path is None else path
    util.open_file(path, "w+", lambda f: parser.write(f))
    if key is not None:
        print("'{}' has been successfully updated".format(key))


def _verify_config_file(path):
    keys = ConfigurationKeys
    config_parser = ConfigParser()
    config_parser.read(path)
    sections = config_parser.sections()
    return keys.USER_SECTION in sections and keys.INTERNAL_SECTION in sections
