from __future__ import print_function

from getpass import getpass

import keyring

from code42cli.profile.config import get_config_accessor, ConfigAccessor

_ROOT_SERVICE_NAME = u"code42cli"


def get_stored_password(profile_name):
    """Gets your currently stored password for the given profile name."""
    profile = _get_profile(profile_name)
    service_name = _get_service_name(profile.name)
    username = _get_username(profile)
    password = keyring.get_password(service_name, username)
    return password


def get_password_from_prompt():
    """Prompts you and returns what you input."""
    return getpass()


def set_password(profile_name, new_password):
    """Sets your password for the given profile name."""
    profile = _get_profile(profile_name)
    service_name = _get_service_name(profile.name)
    username = _get_username(profile)
    keyring.set_password(service_name, username, new_password)
    print(u"'Code42 Password' updated.")


def _get_profile(profile_name):
    accessor = get_config_accessor()
    return accessor.get_profile(profile_name)


def _get_service_name(profile_name):
    return u"{}::{}".format(_ROOT_SERVICE_NAME, profile_name)


def _get_username(profile):
    return profile[ConfigAccessor.USERNAME_KEY]
