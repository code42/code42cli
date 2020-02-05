import keyring
import c42sec.profile._config as config
from c42sec.profile._config import ConfigurationKeys


_ROOT_SERVICE_NAME = u"c42sec"


def get_password():
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    return keyring.get_password(service_name, username)


def set_password(password):
    profile = config.get_config_profile()
    service_name = _get_service_name(profile)
    username = _get_username(profile)
    keyring.set_password(service_name, username, password)


def _get_service_name(profile):
    authority_url = profile[ConfigurationKeys.AUTHORITY_KEY]
    return "{}::{}".format(_ROOT_SERVICE_NAME, authority_url)


def _get_username(profile):
    return profile[ConfigurationKeys.USERNAME_KEY]
