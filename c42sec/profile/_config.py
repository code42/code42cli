import os
from configparser import ConfigParser
from c42sec.util import get_user_project_path


class ConfigurationKeys(object):
    SECTION = u"Code42"
    AUTHORITY_KEY = u"c42_authority_url"
    USERNAME_KEY = u"c42_username"
    IGNORE_SSL_ERRORS_KEY = u"ignore_ssl_errors"


def get_config_profile():
    parser = ConfigParser()
    return _get_config_profile_from_parser(parser)


def get_username():
    return get_config_profile()[ConfigurationKeys.USERNAME_KEY]


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
    profile[ConfigurationKeys.IGNORE_SSL_ERRORS_KEY] = str(int(new_value))
    _save(parser)


def get_config_file_path():
    path = "{}/config.cfg".format(get_user_project_path())
    if not os.path.exists(path):
        _create_new_config_file()

    return path


def _get_config_profile_from_parser(parser):
    config_file_path = get_config_file_path()
    parser.read(config_file_path)
    return parser[ConfigurationKeys.SECTION]


def _create_new_config_file():
    config_parser = ConfigParser()
    config_parser[ConfigurationKeys.SECTION] = {}
    config_parser[ConfigurationKeys.SECTION][ConfigurationKeys.AUTHORITY_KEY] = "null"
    config_parser[ConfigurationKeys.SECTION][ConfigurationKeys.USERNAME_KEY] = "null"
    config_parser[ConfigurationKeys.SECTION][ConfigurationKeys.IGNORE_SSL_ERRORS_KEY] = "0"
    config_file_path = get_config_file_path()
    with open(config_file_path, "w+") as config_file:
        config_parser.write(config_file)


def _save(parser):
    path = get_config_file_path()
    with open(path, "w+") as config_file:
        parser.write(config_file)
