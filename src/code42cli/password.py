from getpass import getpass

import keyring

from code42cli import PRODUCT_NAME
from code42cli.util import does_user_agree


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
    uses_file_storage = keyring.get_keyring().priority < 1
    if uses_file_storage and not _prompt_for_alternative_store():
        return

    keyring.set_password(service_name, profile.username, new_password)


def delete_password(profile):
    """Deletes password for the given profile name."""
    service_name = _get_keyring_service_name(profile.name)
    keyring.delete_password(service_name, profile.username)


def _get_keyring_service_name(profile_name):
    return u"{}::{}".format(PRODUCT_NAME, profile_name)


def _prompt_for_alternative_store():
    prompt = u"keyring is unavailable. Would you like to store in secure flat file? (y/n): "
    return does_user_agree(prompt)
