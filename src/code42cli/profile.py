from click import style

import code42cli.password as password
from code42cli.cmds.search.cursor_store import get_all_cursor_stores_for_profile
from code42cli.config import config_accessor
from code42cli.config import ConfigAccessor
from code42cli.config import NoConfigProfileError
from code42cli.errors import Code42CLIError


class Code42Profile:
    def __init__(self, profile):
        self._profile = profile

    @property
    def name(self):
        return self._profile.name

    @property
    def authority_url(self):
        return self._profile[ConfigAccessor.AUTHORITY_KEY]

    @property
    def username(self):
        return self._profile[ConfigAccessor.USERNAME_KEY]

    @property
    def ignore_ssl_errors(self):
        return self._profile[ConfigAccessor.IGNORE_SSL_ERRORS_KEY]

    @property
    def has_stored_password(self):
        stored_password = password.get_stored_password(self)
        return stored_password is not None and stored_password != ""

    def get_password(self):
        pwd = password.get_stored_password(self)
        if not pwd:
            pwd = password.get_password_from_prompt()
        return pwd

    def __str__(self):
        return "{}: Username={}, Authority URL={}".format(
            self.name, self.username, self.authority_url
        )


def _get_profile(profile_name=None):
    """Returns the profile for the given name."""
    config_profile = config_accessor.get_profile(profile_name)
    return Code42Profile(config_profile)


def get_profile(profile_name=None):
    if profile_name is None:
        validate_default_profile()
    try:
        return _get_profile(profile_name)
    except NoConfigProfileError as ex:
        raise Code42CLIError(str(ex), help=CREATE_PROFILE_HELP)


def default_profile_exists():
    try:
        profile = _get_profile()
        return profile.name and profile.name != ConfigAccessor.DEFAULT_VALUE
    except NoConfigProfileError:
        return False


def is_default_profile(name):
    if default_profile_exists():
        default = get_profile()
        return name == default.name


def validate_default_profile():
    if not default_profile_exists():
        existing_profiles = get_all_profiles()
        if not existing_profiles:
            raise Code42CLIError("No existing profile.", help=CREATE_PROFILE_HELP)
        else:
            raise Code42CLIError(
                "No default profile set.",
                help=_get_set_default_profile_help(existing_profiles),
            )


def profile_exists(profile_name=None):
    try:
        _get_profile(profile_name)
        return True
    except NoConfigProfileError:
        return False


def switch_default_profile(profile_name):
    profile = get_profile(profile_name)  # Handles if profile does not exist.
    config_accessor.switch_default_profile(profile.name)


def create_profile(name, server, username, ignore_ssl_errors):
    if profile_exists(name):
        raise Code42CLIError("A profile named '{}' already exists.".format(name))
    config_accessor.create_profile(name, server, username, ignore_ssl_errors)


def delete_profile(profile_name):
    profile = _get_profile(profile_name)
    profile_name = profile.name
    if password.get_stored_password(profile) is not None:
        password.delete_password(profile)
    cursor_stores = get_all_cursor_stores_for_profile(profile_name)
    for store in cursor_stores:
        store.clean()
    config_accessor.delete_profile(profile_name)


def update_profile(name, server, username, ignore_ssl_errors):
    config_accessor.update_profile(name, server, username, ignore_ssl_errors)


def get_all_profiles():
    profiles = [
        Code42Profile(profile) for profile in config_accessor.get_all_profiles()
    ]
    return profiles


def get_stored_password(profile_name=None):
    profile = get_profile(profile_name)
    return password.get_stored_password(profile)


def set_password(new_password, profile_name=None):
    profile = get_profile(profile_name)
    password.set_password(profile, new_password)


CREATE_PROFILE_HELP = "\nTo add a profile, use:\n{}".format(
    style(
        "\tcode42 profile create --name <profile-name> --server <authority-URL> --username <username>\n",
        bold=True,
    )
)


def _get_set_default_profile_help(existing_profiles):
    existing_profiles = [str(profile) for profile in existing_profiles]
    help_msg = """
Use the --profile flag to specify which profile to use.

To set the default profile (used whenever --profile argument is not provided), use:
    {}

Existing profiles:
\t{}""".format(
        style("code42 profile use <profile-name>", bold=True),
        "\n\t".join(existing_profiles),
    )
    return help_msg
