from __future__ import print_function

import os
from configparser import ConfigParser

import code42cli.util as util
from code42cli.compat import str


class ConfigAccessor(object):
    DEFAULT_VALUE = u"__DEFAULT__"
    AUTHORITY_KEY = u"c42_authority_url"
    USERNAME_KEY = u"c42_username"
    IGNORE_SSL_ERRORS_KEY = u"ignore-ssl-errors"
    DEFAULT_PROFILE_IS_COMPLETE = u"default_profile_is_complete"
    DEFAULT_PROFILE = u"default_profile"
    _INTERNAL_SECTION = u"Internal"

    def __init__(self, parser):
        self.parser = parser
        self.path = u"{}config.cfg".format(util.get_user_project_path())
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
        if name not in self.parser.sections() or name == self.DEFAULT_VALUE:
            raise Exception(u"Profile does not exist.")
        return self.parser[name]

    def get_all_profiles(self):
        """Returns all the available profiles."""
        profiles = []
        names = self._get_profile_names()
        for name in names:
            profiles.append(self.get_profile(name))
        return profiles

    def create_profile_if_not_exists(self, name):
        """Creates a new profile if one does not already exist for that name."""
        try:
            self.get_profile(name)
        except Exception as ex:
            if name is not None and name != self.DEFAULT_VALUE:
                self._create_profile_section(name)
            else:
                raise ex

    def switch_default_profile(self, new_default_name):
        """Changes what is marked as the default profile in the internal section."""
        if self.get_profile(new_default_name) is None:
            raise Exception(u"Profile does not exist.")
        self._internal[self.DEFAULT_PROFILE] = new_default_name
        self._save()

    def set_authority_url(self, new_value, profile_name=None):
        """Sets 'authority URL' for a given profile.
        Uses the default profile if name is None.
        """
        profile = self.get_profile(profile_name)
        profile[self.AUTHORITY_KEY] = new_value.strip()
        self._save()
        self._try_complete_setup(profile)

    def set_username(self, new_value, profile_name=None):
        """Sets 'username' for a given profile. Uses the default profile if not given a name."""
        profile = self.get_profile(profile_name)
        profile[self.USERNAME_KEY] = new_value.strip()
        self._save()
        self._try_complete_setup(profile)

    def set_ignore_ssl_errors(self, new_value, profile_name=None):
        """Sets 'ignore_ssl_errors' for a given profile.
        Uses the default profile if name is None.
        """
        profile = self.get_profile(profile_name)
        profile[self.IGNORE_SSL_ERRORS_KEY] = str(new_value)
        self._save()

    @property
    def _internal(self):
        """The internal section of the config file."""
        return self.parser[self._INTERNAL_SECTION]

    @property
    def _default_profile_name(self):
        return self._internal[self.DEFAULT_PROFILE]

    def _get_profile_names(self):
        names = list(self.parser.sections())
        names.remove(self._INTERNAL_SECTION)
        return names

    def _create_internal_section(self):
        self.parser.add_section(self._INTERNAL_SECTION)
        self.parser[self._INTERNAL_SECTION] = {}
        self.parser[self._INTERNAL_SECTION][self.DEFAULT_PROFILE_IS_COMPLETE] = str(False)
        self.parser[self._INTERNAL_SECTION][self.DEFAULT_PROFILE] = self.DEFAULT_VALUE

    def _create_profile_section(self, name):
        self.parser.add_section(name)
        self.parser[name] = {}
        self.parser[name][self.AUTHORITY_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.USERNAME_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.IGNORE_SSL_ERRORS_KEY] = str(False)
        default_profile = self._internal.get(self.DEFAULT_PROFILE)
        if default_profile is None or default_profile is self.DEFAULT_VALUE:
            self._internal[self.DEFAULT_PROFILE] = name

    def _save(self):
        util.open_file(self.path, u"w+", lambda file: self.parser.write(file))

    def _try_complete_setup(self, profile):
        if self._internal.getboolean(self.DEFAULT_PROFILE_IS_COMPLETE):
            return

        authority = profile.get(self.AUTHORITY_KEY)
        username = profile.get(self.USERNAME_KEY)

        authority_valid = authority and authority != self.DEFAULT_VALUE
        username_valid = username and username != self.DEFAULT_VALUE

        if not authority_valid or not username_valid:
            return

        self._internal[self.DEFAULT_PROFILE_IS_COMPLETE] = str(True)
        if self._internal[self.DEFAULT_PROFILE] == self.DEFAULT_VALUE:
            self._internal[self.DEFAULT_PROFILE] = profile.name

        self._save()


def get_config_accessor():
    """Create a ConfigAccessor with a ConfigParser as its parser."""
    return ConfigAccessor(ConfigParser())
