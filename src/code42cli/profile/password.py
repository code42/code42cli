from __future__ import print_function

from getpass import getpass

import keyring

from code42cli.profile.config import get_config_accessor, ConfigAccessor

_ROOT_SERVICE_NAME = u"code42cli"


def get_password(profile_name):
    """Gets your currently stored password for your profile."""
    profile = _get_profile(profile_name)
    service_name = _get_service_name(profile_name)
    username = _get_username(profile)
    password = keyring.get_password(service_name, username)
    return password


def set_password(profile_name, new_password):
    profile = _get_profile(profile_name)
    service_name = _get_service_name(profile_name)
    username = _get_username(profile)
    keyring.set_password(service_name, username, new_password)
    print(u"'Code42 Password' updated.")


def set_password_from_prompt(profile_name):
    """Prompts and sets your password for your profile."""
    password = getpass()
    set_password(profile_name, password)
    return password


def get_password_from_prompt():
    return getpass()


def _get_profile(profile_name):
    accessor = get_config_accessor()
    return accessor.get_profile(profile_name)


def _get_service_name(profile_name):
    return u"{}::{}".format(_ROOT_SERVICE_NAME, profile_name)


def _get_username(profile):
    return profile[ConfigAccessor.USERNAME_KEY]
