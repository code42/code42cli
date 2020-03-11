from __future__ import print_function

import os
from configparser import ConfigParser

import code42cli.util as util
from code42cli.compat import str

_PROFILE_ENV_VAR_NAME = u"CODE42CLI_PROFILE"


class ConfigParserAccessor(object):
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

    @property
    def internal(self):
        return self.parser[self._INTERNAL_SECTION]

    @property
    def default_profile_name(self):
        return self.internal[self.DEFAULT_PROFILE]

    def get_profile_names(self):
        names = list(self.parser.sections())
        names.remove(self._INTERNAL_SECTION)
        return names

    def has_setup_default_profile(self):
        return not len(self.get_profile_names())

    def get_profile(self, name=None):
        name = name or self.default_profile_name
        if name not in self.parser.sections() and name != self.DEFAULT_VALUE:
            return None
        return self.parser[name]

    def set_authority_url(self, new_value, profile_name=None):
        profile = self.get_profile(profile_name)
        profile[self.AUTHORITY_KEY] = new_value
        self._save()
        self._try_complete_setup()

    def set_username(self, new_value, profile_name=None):
        profile = self.get_profile(profile_name)
        profile[self.USERNAME_KEY] = new_value
        self._save()
        self._try_complete_setup()

    def set_ignore_ssl_errors(self, new_value, profile_name=None):
        profile = self.get_profile(profile_name)
        profile[self.IGNORE_SSL_ERRORS_KEY] = str(new_value)
        self._save()

    def get_all_profiles(self):
        profiles = []
        names = self.get_profile_names()
        for name in names:
            profiles.append(self.get_profile(name))
        return profiles

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
        default_profile = self.internal.get(self.DEFAULT_PROFILE)
        if default_profile is None or default_profile is self.DEFAULT_VALUE:
            self.internal[self.DEFAULT_PROFILE] = name

    def _save(self):
        path = _get_config_file_path()
        util.open_file(path, u"w+", lambda f: self.parser.write(f))

    def _try_complete_setup(self):
        if self.internal.getboolean(self.DEFAULT_PROFILE_IS_COMPLETE):
            return

        default_profile = get_profile()
        if not default_profile:
            return

        authority = default_profile.get(self.AUTHORITY_KEY)
        username = default_profile.get(self.USERNAME_KEY)

        authority_valid = authority is not None and authority != self.DEFAULT_VALUE
        username_valid = username is not None and username != self.DEFAULT_VALUE

        if not authority_valid or not username_valid:
            return

        self.internal[self.DEFAULT_PROFILE_IS_COMPLETE] = str(True)
        if self.internal[self.DEFAULT_PROFILE] == self.DEFAULT_VALUE:
            self.internal[self.DEFAULT_PROFILE] = default_profile.name

        self._save()


def _get_parser_accessor():
    return ConfigParserAccessor(ConfigParser())


def get_profile(profile_name=None):
    accessor = _get_parser_accessor()
    if not accessor.has_setup_default_profile:
        util.print_no_existing_profile_message()
        exit(1)

    profile = accessor.get_profile(profile_name)
    if not profile:
        util.print_no_existing_profile_message()
        exit(1)

    return profile


def write_authority_url(new_url, profile_name=None):
    accessor = _get_parser_accessor()
    accessor.set_authority_url(new_url, profile_name)
    _log_key_save(ConfigParserAccessor.AUTHORITY_KEY)


def write_username(new_username, profile_name=None):
    accessor = _get_parser_accessor()
    accessor.set_username(new_username, profile_name)
    _log_key_save(ConfigParserAccessor.USERNAME_KEY)


def write_ignore_ssl_errors(new_value, profile_name=None):
    accessor = _get_parser_accessor()
    accessor.set_ignore_ssl_errors(new_value, profile_name)
    _log_key_save(ConfigParserAccessor.USERNAME_KEY)





def change_default_profile(profile_name):
    if profile_name not in _get_all_profile_names():
        _print_profile_not_exists_message(profile_name)
        exit(1)
    internal_section = _get_internal_section()
    internal_section[ConfigurationKeys.DEFAULT_PROFILE] = profile_name

def _print_profile_not_exists_message(profile_name):
    util.print_error(u"Profile '{0}' does not exist.".format(profile_name))


def _log_key_save(key):
    if key == ConfigParserAccessor.DEFAULT_PROFILE_IS_COMPLETE:
        print(u"You have completed setting up your profile!")
    else:
        print(u"'{}' has been successfully updated".format(key))

