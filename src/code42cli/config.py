import os

from configparser import ConfigParser

import code42cli.util as util
from code42cli.compat import str
from code42cli.logger import get_main_cli_logger


class NoConfigProfileError(Exception):
    def __init__(self, profile_arg_name=None):
        message = (
            u"Profile '{}' does not exist.".format(profile_arg_name)
            if profile_arg_name
            else u"Profile does not exist."
        )
        super(NoConfigProfileError, self).__init__(message)


class ConfigAccessor(object):
    DEFAULT_VALUE = u"__DEFAULT__"
    AUTHORITY_KEY = u"c42_authority_url"
    USERNAME_KEY = u"c42_username"
    IGNORE_SSL_ERRORS_KEY = u"ignore-ssl-errors"
    DEFAULT_PROFILE = u"default_profile"
    _INTERNAL_SECTION = u"Internal"

    def __init__(self, parser):
        self.parser = parser
        file_name = u"config.cfg"
        self.path = os.path.join(util.get_user_project_path(), file_name)
        if not os.path.exists(self.path):
            self._create_internal_section()
            self._save()
        else:
            self.parser.read(self.path)

    def get_profile(self, name=None):
        """Returns the profile with the given name.
        If name is None, returns the default profile.
        If the name does not exist or there is no existing profile, it will throw an exception.
        """
        name = name or self._default_profile_name
        if name not in self._get_sections() or name == self.DEFAULT_VALUE:
            name = name if name != self.DEFAULT_VALUE else None
            raise NoConfigProfileError(name)
        return self._get_profile(name)

    def get_all_profiles(self):
        """Returns all the available profiles."""
        profiles = []
        names = self._get_profile_names()
        for name in names:
            profiles.append(self.get_profile(name))
        return profiles

    def create_profile(self, name, server, username, ignore_ssl_errors):
        """Creates a new profile if one does not already exist for that name."""
        try:
            self.get_profile(name)
        except NoConfigProfileError as ex:
            if name is not None and name != self.DEFAULT_VALUE:
                self._create_profile_section(name)
            else:
                raise ex

        profile = self.get_profile(name)
        self.update_profile(profile.name, server, username, ignore_ssl_errors)
        self._try_complete_setup(profile)

    def update_profile(self, name, server=None, username=None, ignore_ssl_errors=None):
        profile = self.get_profile(name)
        if server:
            self._set_authority_url(server, profile)
        if username:
            self._set_username(username, profile)
        if ignore_ssl_errors is not None:
            self._set_ignore_ssl_errors(ignore_ssl_errors, profile)
        self._save()

    def switch_default_profile(self, new_default_name):
        """Changes what is marked as the default profile in the internal section."""
        if self.get_profile(new_default_name) is None:
            raise NoConfigProfileError(new_default_name)
        self._internal[self.DEFAULT_PROFILE] = new_default_name
        self._save()
        get_main_cli_logger().print_info(
            u"{} has been set as the default profile.".format(new_default_name)
        )

    def delete_profile(self, name):
        """Deletes a profile."""
        if self.get_profile(name) is None:
            raise NoConfigProfileError(name)
        self.parser.remove_section(name)
        if name == self._default_profile_name:
            self._internal[self.DEFAULT_PROFILE] = self.DEFAULT_VALUE
        self._save()

    def _set_authority_url(self, new_value, profile):
        profile[self.AUTHORITY_KEY] = new_value.strip()

    def _set_username(self, new_value, profile):
        profile[self.USERNAME_KEY] = new_value.strip()

    def _set_ignore_ssl_errors(self, new_value, profile):
        profile[self.IGNORE_SSL_ERRORS_KEY] = str(new_value)

    def _get_sections(self):
        return self.parser.sections()

    def _get_profile(self, name):
        return self.parser[name]

    @property
    def _internal(self):
        return self.parser[self._INTERNAL_SECTION]

    @property
    def _default_profile_name(self):
        return self._internal[self.DEFAULT_PROFILE]

    def _get_profile_names(self):
        names = list(self._get_sections())
        names.remove(self._INTERNAL_SECTION)
        return names

    def _create_internal_section(self):
        self.parser.add_section(self._INTERNAL_SECTION)
        self.parser[self._INTERNAL_SECTION] = {}
        self.parser[self._INTERNAL_SECTION][self.DEFAULT_PROFILE] = self.DEFAULT_VALUE

    def _create_profile_section(self, name):
        self.parser.add_section(name)
        self.parser[name] = {}
        self.parser[name][self.AUTHORITY_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.USERNAME_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.IGNORE_SSL_ERRORS_KEY] = str(False)

    def _save(self):
        util.open_file(self.path, u"w+", lambda file: self.parser.write(file))

    def _try_complete_setup(self, profile):
        authority = profile.get(self.AUTHORITY_KEY)
        username = profile.get(self.USERNAME_KEY)

        authority_valid = authority and authority != self.DEFAULT_VALUE
        username_valid = username and username != self.DEFAULT_VALUE

        if not authority_valid or not username_valid:
            return

        self._save()
        get_main_cli_logger().print_info(u"Successfully saved profile '{}'.".format(profile.name))

        default_profile = self._internal.get(self.DEFAULT_PROFILE)
        if default_profile is None or default_profile == self.DEFAULT_VALUE:
            self.switch_default_profile(profile.name)


config_accessor = ConfigAccessor(ConfigParser())
