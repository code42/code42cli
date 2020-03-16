from __future__ import print_function

from argparse import RawDescriptionHelpFormatter

import code42cli.arguments as main_args
import code42cli.profile.password as password
from code42cli.compat import str
from code42cli.profile.config import get_config_accessor, ConfigAccessor
from code42cli.sdk_client import validate_connection
from code42cli.util import (
    does_user_agree,
    print_error,
    print_set_profile_help,
    print_no_existing_profile_message,
)


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
    def ignore_ssl_error(self):
        return self._profile[ConfigAccessor.IGNORE_SSL_ERRORS_KEY]

    def get_password(self):
        pwd = password.get_stored_password(self.name)
        if not pwd:
            pwd = password.get_password_from_prompt()
        return pwd

    def __str__(self):
        return u"{0}: Username={1}, Authority URL={2}".format(
            self.name, self.username, self.authority_url
        )


def init(subcommand_parser):
    """Sets up the `profile` subcommand with `show` and `set` subcommands.
            `show` will print the current profile while `set` will modify profile properties.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """

    description = u"""
    Subcommands:
          show      - Print the details of a profile.
          set       - Create or update profile settings. The first profile created will be the default.
          reset-pw  - Change the stored password for a profile.
          list      - Show all existing stored profiles.
          use       - Set a profile as the default.
    """
    parser_profile = subcommand_parser.add_parser(
        u"profile",
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        usage=u"code42 profile <subcommand> <optional args>",
    )
    profile_subparsers = parser_profile.add_subparsers(title="subcommands")

    parser_for_show = profile_subparsers.add_parser(
        u"show",
        description=u"Print the details of a profile.",
        usage=u"code42 profile show <optional-args>",
    )
    parser_for_set = profile_subparsers.add_parser(
        u"set",
        description=u"Create or update profile settings. The first profile created will be the default.",
        usage=u"code42 profile set <optional-args>",
    )
    parser_for_reset_password = profile_subparsers.add_parser(
        u"reset-pw",
        description=u"Change the stored password for a profile.",
        usage=u"code42 profile reset-pw <optional-args>",
    )
    parser_for_list = profile_subparsers.add_parser(
        u"list",
        description=u"Show all existing stored profiles.",
        usage=u"code42 profile list <optional-args>",
    )
    parser_for_use = profile_subparsers.add_parser(
        u"use",
        description=u"Set a profile as the default.",
        usage=u"code42 profile use <profile-name>",
    )

    parser_for_show.set_defaults(func=show_profile)
    parser_for_set.set_defaults(func=set_profile)
    parser_for_reset_password.set_defaults(func=prompt_for_password_reset)
    parser_for_list.set_defaults(func=list_profiles)
    parser_for_use.set_defaults(func=use_profile)

    main_args.add_profile_name_arg(parser_for_show)
    main_args.add_profile_name_arg(parser_for_reset_password)
    _add_args_to_set_command(parser_for_set)
    _add_positional_profile_arg(parser_for_use)


def get_profile(profile_name=None):
    """Returns the profile for the given name."""
    accessor = get_config_accessor()
    try:
        profile = accessor.get_profile(profile_name)
        return Code42Profile(profile)
    except Exception as ex:
        print_error(str(ex))
        print_set_profile_help()
        exit(1)


def show_profile(args):
    """Prints the given profile to stdout."""
    profile = get_profile(args.profile_name)
    print(u"\n{0}:".format(profile.name))
    print(u"\t* {0} = {1}".format(ConfigAccessor.USERNAME_KEY, profile.username))
    print(u"\t* {0} = {1}".format(ConfigAccessor.AUTHORITY_KEY, profile.authority_url))
    print(u"\t* {0} = {1}".format(ConfigAccessor.IGNORE_SSL_ERRORS_KEY, profile.ignore_ssl_error))
    if password.get_stored_password(profile.name) is not None:
        print(u"\t* A password is set.")
    print(u"")


def set_profile(args):
    """Sets the given profile using command line arguments."""
    _verify_args_for_set(args)
    accessor = get_config_accessor()
    accessor.create_profile_if_not_exists(args.profile_name)
    _try_set_authority_url(args, accessor)
    _try_set_username(args, accessor)
    _try_set_ignore_ssl_errors(args, accessor)
    _prompt_for_allow_password_set(args)


def prompt_for_password_reset(args):
    """Securely prompts for your password and then stores it using keyring."""
    profile = get_profile(args.profile_name)
    new_password = password.get_password_from_prompt()

    if not validate_connection(profile.authority_url, profile.username, new_password):
        print_error(
            "Your password was not saved because your credentials failed to validate. "
            "Check your network connection and the spelling of your username and server URL."
        )
        exit(1)
    password.set_password(profile.name, new_password)


def list_profiles(*args):
    """Lists all profiles that exist for this OS user."""
    accessor = get_config_accessor()
    profiles = accessor.get_all_profiles()
    if not profiles:
        print_no_existing_profile_message()
        return
    for profile in profiles:
        profile = Code42Profile(profile)
        print(profile)


def use_profile(args):
    """Changes the default profile to the given one."""
    accessor = get_config_accessor()
    try:
        accessor.switch_default_profile(args.profile_name)
    except Exception as ex:
        print_error(str(ex))
        exit(1)


def _add_args_to_set_command(parser_for_set):
    main_args.add_profile_name_arg(parser_for_set)
    _add_authority_arg(parser_for_set)
    _add_username_arg(parser_for_set)
    _add_disable_ssl_errors_arg(parser_for_set)
    _add_enable_ssl_errors_arg(parser_for_set)


def _add_positional_profile_arg(parser):
    parser.add_argument(
        action=u"store", dest=main_args.PROFILE_NAME_KEY, help=main_args.PROFILE_HELP_MESSAGE
    )


def _add_authority_arg(parser):
    parser.add_argument(
        u"-s",
        u"--server",
        action=u"store",
        dest=ConfigAccessor.AUTHORITY_KEY,
        help=u"The full scheme, url and port of the Code42 server.",
    )


def _add_username_arg(parser):
    parser.add_argument(
        u"-u",
        u"--username",
        action=u"store",
        dest=ConfigAccessor.USERNAME_KEY,
        help=u"The username of the Code42 API user.",
    )


def _add_disable_ssl_errors_arg(parser):
    parser.add_argument(
        u"--disable-ssl-errors",
        action=u"store_true",
        default=None,
        dest=u"disable_ssl_errors",
        help=u"For development purposes, do not validate the SSL certificates of Code42 servers."
        u"This is not recommended unless it is required.",
    )


def _add_enable_ssl_errors_arg(parser):
    parser.add_argument(
        u"--enable-ssl-errors",
        action=u"store_true",
        default=None,
        dest=u"enable_ssl_errors",
        help=u"Do validate the SSL certificates of Code42 servers.",
    )


def _verify_args_for_set(args):
    if _missing_default_profile(args):
        print_error(u"Must supply a name when setting your profile for the first time.")
        print_set_profile_help()
        exit(1)

    missing_values = not args.c42_username and not args.c42_authority_url
    if missing_values:
        try:
            accessor = get_config_accessor()
            profile = Code42Profile(accessor.get_profile(args.profile_name))
            missing_values = not profile.username and not profile.authority_url
        except Exception:
            missing_values = True

    if missing_values:
        print_error(u"Missing username and authority url.")
        print_set_profile_help()
        exit(1)


def _try_set_authority_url(args, accessor):
    if args.c42_authority_url is not None:
        accessor.set_authority_url(args.c42_authority_url, args.profile_name)


def _try_set_username(args, accessor):
    if args.c42_username is not None:
        accessor.set_username(args.c42_username, args.profile_name)


def _try_set_ignore_ssl_errors(args, accessor):
    if args.disable_ssl_errors is not None and not args.enable_ssl_errors:
        accessor.set_ignore_ssl_errors(True, args.profile_name)

    if args.enable_ssl_errors is not None:
        accessor.set_ignore_ssl_errors(False, args.profile_name)


def _missing_default_profile(args):
    profile_name_arg_is_none = (
        args.profile_name is None or args.profile_name == ConfigAccessor.DEFAULT_VALUE
    )
    return profile_name_arg_is_none and not _default_profile_exist()


def _default_profile_exist():
    try:
        accessor = get_config_accessor()
        profile = Code42Profile(accessor.get_profile())
        return profile.name and profile.name != ConfigAccessor.DEFAULT_VALUE
    except Exception:
        return False


def _prompt_for_allow_password_set(args):
    if does_user_agree(u"Would you like to set a password? (y/n): "):
        prompt_for_password_reset(args)


def _log_key_save(key):
    if key == ConfigAccessor.DEFAULT_PROFILE_IS_COMPLETE:
        print(u"You have completed setting up your profile!")
    else:
        print(u"'{}' has been successfully updated".format(key))
