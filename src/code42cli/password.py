from __future__ import print_function
from getpass import getpass

import keyring

from code42cli.config import ConfigAccessor

_ROOT_SERVICE_NAME = u"code42cli"


def get_stored_password(profile):
    """Gets your currently stored password for the given profile name."""
    service_name = _get_keyring_service_name(profile.name)
    return keyring.get_password(service_name, profile.username)


def get_password_from_prompt():
    """Prompts you and returns what you input."""
    return getpass()


def set_password(profile, new_password):
    """Sets your password for the given profile name."""
    service_name = _get_keyring_service_name(profile.name)
    keyring.set_password(service_name, profile.username, new_password)


def _get_keyring_service_name(profile_name):
    return u"{}::{}".format(_ROOT_SERVICE_NAME, profile_name)
