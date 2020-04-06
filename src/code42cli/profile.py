import code42cli.password as password
from code42cli.config import ConfigAccessor, get_config_accessor
from code42cli.util import print_error, print_set_profile_help


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
    accessor = get_config_accessor()
    return Code42Profile(accessor.get_profile(profile_name))


def get_profile(profile_name=None):
    try:
        return _get_profile(profile_name)
    except Exception as ex:
        print_error(str(ex))
        print_set_profile_help()
        exit(1)


def default_profile_exists():
    try:
        profile = _get_profile()
        return profile.name and profile.name != ConfigAccessor.DEFAULT_VALUE
    except Exception:
        return False


def profile_exists(profile_name=None):
    try:
        _get_profile(profile_name)
        return True
    except Exception:
        return False


def switch_default_profile(profile_name):
    config = get_config_accessor()
    config.switch_default_profile(profile_name)


def create_profile(name, server, username, ignore_ssl_errors):
    config = get_config_accessor()
    config.create_profile(name, server, username, ignore_ssl_errors)


def get_all_profiles():
    config = get_config_accessor()
    profiles = [Code42Profile(profile) for profile in config.get_all_profiles()]
    return profiles


def get_stored_password(profile_name=None):
    profile = get_profile(profile_name)
    return password.get_stored_password(profile)


def set_password(new_password, profile_name=None):
    profile = get_profile(profile_name)
    password.set_password(profile, new_password)
