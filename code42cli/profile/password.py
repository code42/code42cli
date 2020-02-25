from __future__ import print_function
import keyring
from getpass import getpass

import code42cli.profile.config as config
from code42cli.profile.config import ConfigurationKeys


_ROOT_SERVICE_NAME = u"code42cli"


def get_password(prompt_if_not_exists=True):
    """Gets your currently stored password for your username / authority URL combo."""
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    password = keyring.get_password(service_name, username)
    if password is None and prompt_if_not_exists:
        return set_password()

    return password


def set_password():
    """Prompts and sets your password for your username / authority URL combo."""
    password = getpass()
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    keyring.set_password(service_name, username, password)
    print("'Code42 Password' updated.")
    return password


def _get_service_name(profile):
    authority_url = profile[ConfigurationKeys.AUTHORITY_KEY]
    return "{}::{}".format(_ROOT_SERVICE_NAME, authority_url)


def _get_username(profile):
    return profile[ConfigurationKeys.USERNAME_KEY]
