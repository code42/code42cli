import keyring
from c42sec.profile._config import get_username


_SERVICE_NAME = u"c42sec"


def get_password():
    username = get_username()
    return keyring.get_password(_SERVICE_NAME, username)


def set_password(password):
    username = get_username()
    keyring.set_password(_SERVICE_NAME, username, password)
