import keyring
from getpass import getpass
import c42sec.profile._config as config
from c42sec.profile._config import ConfigurationKeys


_ROOT_SERVICE_NAME = u"c42sec"


def get_password(prompt_if_not_exists=True):
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    password = keyring.get_password(service_name, username)
    if password is None and prompt_if_not_exists:
        return set_password()

    return password


def set_password():
    password = getpass()
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    keyring.set_password(service_name, username, password)
    return password


def _get_service_name(profile):
    authority_url = profile[ConfigurationKeys.AUTHORITY_KEY]
    return "{}::{}".format(_ROOT_SERVICE_NAME, authority_url)


def _get_username(profile):
    return profile[ConfigurationKeys.USERNAME_KEY]
