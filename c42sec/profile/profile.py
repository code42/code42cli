from argparse import ArgumentParser
from c42sec.profile._config import (
    get_config_profile,
    set_authority_url,
    set_username,
    set_ignore_ssl_errors,
    ConfigurationKeys,
)
from c42sec.profile._password import get_password, set_password


def init(parent_parser):
    # type: (ArgumentParser) -> None
    """Sets up the `profile` command with `show` and `set` subcommands.
            `show` will print the current profile while `set` will modify profile properties.
            Use `-h` after any subcommand for usage.
        Args:
            parent_parser: The parser for the CLI command before this one (c42sec)
    """
    subparsers = parent_parser.add_subparsers()
    parser_profile = subparsers.add_parser("profile")
    parser_profile.set_defaults(func=show_profile)
    profile_subparsers = parser_profile.add_subparsers()

    parser_show = profile_subparsers.add_parser("show")
    parser_set = profile_subparsers.add_parser("set")

    parser_show.set_defaults(func=show_profile)
    parser_set.set_defaults(func=set_profile)
    _add_set_command_args(parser_set)


def get_profile():
    """Returns the current profile as a dict"""
    profile = get_config_profile()
    profile[ConfigurationKeys.PASSWORD_KEY] = get_password()
    return profile


def show_profile(*args):
    """Prints the current profile to stdout."""
    profile = get_config_profile()
    print()
    print("Current profile:")
    print("========================")
    for key in profile:
        print("{} = {}".format(key, profile[key]))

    if get_password() is not None:
        print()
        print("A password exists for this profile.")

    print()


def set_profile(args):
    """Sets the current profile using command line arguments."""

    if args.c42_authority_url is not None:
        set_authority_url(args.c42_authority_url)
        print("'Code42 authority URL' saved. New value: {}".format(args.c42_authority_url))

    if args.c42_username is not None:
        set_username(args.c42_username)
        print("'Code42 username' saved. New value: {}".format(args.c42_username))

    if args.ignore_ssl_errors is not None:
        set_ignore_ssl_errors(args.ignore_ssl_errors)
        print("'Ignore SSL errors' saved. New value: {}".format(args.ignore_ssl_errors))

    # Must happen after setting password
    if args.c42_password is not None:
        set_password(args.c42_password)
        print("'Code42 Password' saved.")


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
        action="store",
        dest=ConfigurationKeys.PASSWORD_KEY,
        help="The password for the Code42 API user. "
        "Note: if you don't supply a password, you will be prompted. "
        "Passwords are not stored in plain text.",
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
