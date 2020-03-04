from __future__ import print_function
import keyring
from getpass import getpass

import code42cli.profile.config as config
from code42cli.profile.config import ConfigurationKeys


_ROOT_SERVICE_NAME = u"code42cli"


def get_password():
    """Gets your currently stored password for your username / authority URL combo."""
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    password = keyring.get_password(service_name, username)
    return password


def set_password_from_prompt():
    """Prompts and sets your password for your username / authority URL combo."""
    password = getpass()
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    keyring.set_password(service_name, username, password)
    print(u"'Code42 Password' updated.")
    return password


def get_password_from_prompt():
    return getpass()


def _get_service_name(profile):
    authority_url = profile[ConfigurationKeys.AUTHORITY_KEY]
    return u"{}::{}".format(_ROOT_SERVICE_NAME, authority_url)


def _get_username(profile):
    return profile[ConfigurationKeys.USERNAME_KEY]
