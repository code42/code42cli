from __future__ import print_function

from getpass import getpass
import keyring

from code42cli.profile.config import get_config_accessor, ConfigAccessor
from code42cli.util import does_user_agree, open_file, get_user_project_path

_ROOT_SERVICE_NAME = u"code42cli"


def get_stored_password(profile_name):
    """Gets your currently stored password for the given profile name."""
    profile = _get_profile(profile_name)
    return _get_stored_password(profile)


def get_password_from_prompt():
    """Prompts you and returns what you input."""
    return getpass()


def set_password(profile_name, new_password):
    """Sets your password for the given profile name."""
    profile = _get_profile(profile_name)
    service_name = _get_keyring_service_name(profile.name)
    username = _get_username(profile)
    _store_password(profile, service_name, username, new_password)
    print(u"'Code42 Password' updated.")


def _get_profile(profile_name):
    accessor = get_config_accessor()
    return accessor.get_profile(profile_name)


def _get_stored_password(profile):
    password_from_keyring = _get_password_from_keyring(profile)
    return password_from_keyring or _get_password_from_file(profile)


def _get_keyring_service_name(profile_name):
    return u"{}::{}".format(_ROOT_SERVICE_NAME, profile_name)


def _get_password_from_keyring(profile):
    try:
        service_name = _get_keyring_service_name(profile.name)
        username = _get_username(profile)
        return keyring.get_password(service_name, username)
    except:
        return None


def _get_password_from_file(profile):
    path = _get_password_file_path(profile)
    def read_password(file):
        try:
            return file.readline(file)
        except IOError:
            return None

    return open_file(path, u"r", lambda file: read_password(file))


def _store_password(profile, service_name, username, new_password):
    if not _store_password_using_keyring(service_name, username, new_password):
        _store_password_using_file(profile, new_password)


def _store_password_using_keyring(service_name, username, new_password):
    try:
        keyring.set_password(service_name, username, new_password)
        was_successful = keyring.get_password(service_name, username) is not None
        return was_successful
    except:
        return False


def _store_password_using_file(profile, new_password):
    save_to_file = _prompt_for_alternative_store()
    if save_to_file:
        path = _get_password_file_path(profile)
        def write_password(file):
            file.truncate(0)
            file.write(new_password)
        open_file(path, u"w+", lambda file: write_password(file))


def _get_password_file_path(profile):
    project_path = get_user_project_path()
    return u"{0}.{1}".format(project_path, profile.name)


def _get_username(profile):
    return profile[ConfigAccessor.USERNAME_KEY]


def _prompt_for_alternative_store():
    prompt = u"keyring is unavailable. Would you like to store in secure flat file? (y/n): "
    return does_user_agree(prompt)
