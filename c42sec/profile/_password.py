import keyring
from c42sec.profile._config import get_config_profile, ConfigurationKeys


_SERVICE_NAME = u"c42sec"


def get_password():
    return keyring.get_password(_SERVICE_NAME, _get_key())


def set_password(password):
    keyring.set_password(_SERVICE_NAME, _get_key(), password)


def _get_key():
    profile = get_config_profile()
    username = profile[ConfigurationKeys.USERNAME_KEY]
    authority_url = profile[ConfigurationKeys.AUTHORITY_KEY]
    return "{}-{}".format(username, authority_url)
