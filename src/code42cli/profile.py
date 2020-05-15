from code42cli.compat import str
import code42cli.password as password
from code42cli.cmds.search_shared.cursor_store import get_all_cursor_stores_for_profile
from code42cli.config import ConfigAccessor, config_accessor, NoConfigProfileError
from code42cli.logger import get_main_cli_logger


class Code42Profile(object):
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
        return stored_password is not None and stored_password != u""

    def get_password(self):
        pwd = password.get_stored_password(self)
        if not pwd:
            pwd = password.get_password_from_prompt()
        return pwd

    def __str__(self):
        return u"{0}: Username={1}, Authority URL={2}".format(
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
        logger = get_main_cli_logger()
        logger.print_and_log_error(str(ex))
        _print_create_profile_help()
        exit(1)


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
            print_and_log_no_existing_profile()
        else:
            _print_set_default_profile_help(existing_profiles)
        exit(1)


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
        logger = get_main_cli_logger()
        logger.print_and_log_error(u"A profile named '{}' already exists.".format(name))
        exit(1)

    config_accessor.create_profile(name, server, username, ignore_ssl_errors)


def delete_profile(profile_name):
    profile = _get_profile(profile_name)
    if password.get_stored_password(profile) is not None:
        password.delete_password(profile)
    cursor_stores = get_all_cursor_stores_for_profile(profile_name)
    for store in cursor_stores:
        store.clean()
    config_accessor.delete_profile(profile_name)
    get_main_cli_logger().print_info(u"Profile '{}' has been deleted.".format(profile_name))


def update_profile(name, server, username, ignore_ssl_errors):
    config_accessor.update_profile(name, server, username, ignore_ssl_errors)


def get_all_profiles():
    profiles = [Code42Profile(profile) for profile in config_accessor.get_all_profiles()]
    return profiles


def get_stored_password(profile_name=None):
    profile = get_profile(profile_name)
    return password.get_stored_password(profile)


def set_password(new_password, profile_name=None):
    profile = get_profile(profile_name)
    password.set_password(profile, new_password)


def print_and_log_no_existing_profile():
    logger = get_main_cli_logger()
    logger.print_and_log_error(u"No existing profile.")
    _print_create_profile_help()


def _print_create_profile_help():
    logger = get_main_cli_logger()
    logger.print_info(u"\nTo add a profile, use: ")
    logger.print_bold(u"\tcode42 profile create <profile-name> <authority-URL> <username>\n")


def _print_set_default_profile_help(existing_profiles):
    logger = get_main_cli_logger()
    logger.print_info(
        u"\nNo default profile set.\n"
        u"\nUse the --profile flag to specify which profile to use.\n"
        u"\nTo set the default profile (used whenever --profile argument is not provided), use:"
    )
    logger.print_bold(u"\tcode42 profile use <profile-name>")
    logger.print_info(u"\nExisting profiles:")
    for profile in existing_profiles:
        logger.print_info("\t{}".format(profile))
    logger.print_info(u"")
