from __future__ import print_function

import code42cli.arguments as main_args
import code42cli.profile.config as config
import code42cli.profile.password as password
from code42cli.profile.config import ConfigurationKeys
from code42cli.util import (
    get_input,
    print_error,
    print_set_profile_help,
    print_no_existing_profile_message,
)


class Code42Profile(object):
    def __init__(self, profile_section):
        self.name = profile_section.name
        self.authority_url = profile_section.get(ConfigurationKeys.AUTHORITY_KEY)
        self.username = profile_section.get(ConfigurationKeys.USERNAME_KEY)
        self.ignore_ssl_errors = profile_section.get(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)

    def get_password(self):
        pwd = password.get_password(self.name)
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
    parser_profile = subcommand_parser.add_parser(u"profile")
    profile_subparsers = parser_profile.add_subparsers()

    parser_for_show = profile_subparsers.add_parser(u"show")
    parser_for_set = profile_subparsers.add_parser(u"set")
    parser_for_reset_password = profile_subparsers.add_parser(u"reset-pw")
    parser_for_list = profile_subparsers.add_parser(u"list")
    parser_for_use = profile_subparsers.add_parser(u"use")

    parser_for_show.set_defaults(func=show_profile)
    parser_for_set.set_defaults(func=set_profile)
    parser_for_reset_password.set_defaults(func=prompt_for_password_reset)
    parser_for_list.set_defaults(func=list_profiles)
    parser_for_use.set_defaults(func=use_profile)

    main_args.add_profile_name_arg(parser_for_show)
    _add_args_to_set_command(parser_for_set)
    _add_positional_profile_arg(parser_for_use)


def get_profile(profile_name=None):
    """Returns the current profile object."""
    profile_section = config.get_profile(profile_name)
    return Code42Profile(profile_section)


def show_profile(args):
    """Prints the current profile to stdout."""
    profile = config.get_profile(args.profile_name)
    print(u"\n{0}:".format(profile.name))
    for key in profile:
        print(u"\t* {} = {}".format(key, profile[key]))

    if password.get_password(args.profile_name) is not None:
        print(u"\t* A password is set.")
    print(u"")


def set_profile(args):
    """Sets the current profile using command line arguments."""

    _verify_args_for_set(args)
    _try_set_authority_url(args)
    _try_set_username(args)
    _try_set_ignore_ssl_errors(args)
    _prompt_for_allow_password_set(args)


def prompt_for_password_reset(args):
    """Securely prompts for your password and then stores it using keyring."""
    password.set_password_from_prompt(args.profile_name)


def list_profiles(*args):
    """Lists all profiles that exist for this OS user."""
    profile_sections = config.get_all_profiles()
    if profile_sections:
        for section in profile_sections:
            print(Code42Profile(section))
    else:
        print_no_existing_profile_message()


def use_profile(args):
    config.change_default_profile(args.profile_name)


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
        dest=ConfigurationKeys.AUTHORITY_KEY,
        help=u"The full scheme, url and port of the Code42 server.",
    )


def _add_username_arg(parser):
    parser.add_argument(
        u"-u",
        u"--username",
        action=u"store",
        dest=ConfigurationKeys.USERNAME_KEY,
        help=u"The username of the Code42 API user.",
    )


def _add_disable_ssl_errors_arg(parser):
    parser.add_argument(
        u"--disable-ssl-errors",
        action=u"store_true",
        default=None,
        dest=u"disable_ssl_errors",
        help=u"Do not validate the SSL certificates of Code42 servers.",
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
        print_error("Must supply a name when setting your profile for the first time.")
        print_set_profile_help()
        exit(1)

    missing_values = not args.c42_username and not args.c42_authority_url
    if missing_values:
        try:
            profile = config.get_profile(args.profile_name)
            missing_values = not profile.get(ConfigurationKeys.USERNAME_KEY) and not profile.get(ConfigurationKeys.AUTHORITY_KEY)
        except SystemExit:
            missing_values = False

    if missing_values:
        print_error(u"Missing username and authority url.")
        print_set_profile_help()
        exit(1)


def _try_set_authority_url(args):
    if args.c42_authority_url is not None:
        config.write_authority_url(args.c42_authority_url, args.profile_name)


def _try_set_username(args):
    if args.c42_username is not None:
        config.write_username(args.c42_username, args.profile_name)


def _try_set_ignore_ssl_errors(args):
    if args.disable_ssl_errors is not None and not args.enable_ssl_errors:
        config.write_ignore_ssl_errors(True, args.profile_name)

    if args.enable_ssl_errors is not None:
        config.write_ignore_ssl_errors(False, args.profile_name)


def _missing_default_profile(args):
    profile_name_arg_is_none = (
        args.profile_name is None or args.profile_name == config.DEFAULT_VALUE
    )
    return profile_name_arg_is_none and not _default_profile_exists()


def _default_profile_exists():
    profile_name = config.get_profile().name
    return profile_name is not None and profile_name != config.DEFAULT_VALUE


def _prompt_for_allow_password_set(args):
    answer = get_input(u"Would you like to set a password? (y/n): ")
    if answer.lower() == u"y":
        prompt_for_password_reset(args)
