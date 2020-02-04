from getpass import getpass

from c42sec.profile._config import (
    get_config_profile,
    set_authority_url,
    set_username,
    set_ignore_ssl_errors,
    ConfigurationKeys,
)
from c42sec.profile._password import get_password, set_password


class C42SecProfile(object):
    authority_url = ""
    username = ""
    ignore_ssl_errors = False
    get_password = get_password


def init(subcommand_parser):
    """Sets up the `profile` command with `show` and `set` subcommands.
            `show` will print the current profile while `set` will modify profile properties.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser
    """
    parser_profile = subcommand_parser.add_parser("profile")
    parser_profile.set_defaults(func=show_profile)
    profile_subparsers = parser_profile.add_subparsers()

    parser_show = profile_subparsers.add_parser("show")
    parser_set = profile_subparsers.add_parser("set")

    parser_show.set_defaults(func=show_profile)
    parser_set.set_defaults(func=set_profile)
    _add_set_command_args(parser_set)


def get_profile():
    # type: () -> C42SecProfile
    """Returns the current profile object"""
    profile_values = get_config_profile()
    profile = C42SecProfile()
    profile.authority_url = profile_values.get(ConfigurationKeys.AUTHORITY_KEY)
    profile.username = profile_values.get(ConfigurationKeys.USERNAME_KEY)
    profile.ignore_ssl_errors = bool(int(profile_values.get(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)))
    return profile


def show_profile(*args):
    """Prints the current profile to stdout."""
    profile = get_config_profile()
    print()
    print("Profile:")

    for key in profile:
        print("\t* {} = {}".format(key, profile[key]))

    if get_password() is not None:
        print("\t* A password exists for this profile.")

    print()


def set_profile(args):
    """Sets the current profile using command line arguments."""

    if args.c42_authority_url is not None:
        set_authority_url(args.c42_authority_url)
        print("'Code42 authority URL' updated.".format(args.c42_authority_url))

    if args.c42_username is not None:
        set_username(args.c42_username)
        print("'Code42 username' updated.".format(args.c42_username))

    if args.ignore_ssl_errors is not None:
        set_ignore_ssl_errors(args.ignore_ssl_errors)
        print("'Ignore SSL errors' updated.".format(args.ignore_ssl_errors))

    # Must happen after setting password
    if args.do_set_c42_password:
        password = getpass()
        set_password(password)
        print("'Code42 Password' updated.")

    show_profile()


def _add_set_command_args(parser):
    _add_authority_arg(parser)
    _add_username_arg(parser)
    _add_password_arg(parser)
    _add_ignore_ssl_errors_arg(parser)


def _add_authority_arg(parser):
    parser.add_argument(
        "-s",
        "--server",
        action="store",
        dest=ConfigurationKeys.AUTHORITY_KEY,
        help="The full scheme, url and port of the Code42 server.",
    )


def _add_username_arg(parser):
    parser.add_argument(
        "-u",
        "--username",
        action="store",
        dest=ConfigurationKeys.USERNAME_KEY,
        help="The username of the Code42 API user.",
    )


def _add_password_arg(parser):
    parser.add_argument(
        "-p",
        "--password",
        action="store_true",
        dest="do_set_c42_password",
        help="The password for the Code42 API user. " "Passwords are not stored in plain text.",
    )


def _add_ignore_ssl_errors_arg(parser):
    parser.add_argument(
        "--ignore-ssl-errors",
        action="store_true",
        default=None,
        dest=ConfigurationKeys.IGNORE_SSL_ERRORS_KEY,
        help="Do not validate the SSL certificates of Code42 servers",
    )


if __name__ == "__main__":
    show_profile()
