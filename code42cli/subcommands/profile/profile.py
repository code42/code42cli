from __future__ import print_function

import code42cli.subcommands.profile.config as config
import code42cli.subcommands.profile.password as password
from code42cli.subcommands.profile.config import ConfigurationKeys
from code42cli.util import print_error


class Code42Profile(object):
    authority_url = ""
    username = ""
    ignore_ssl_errors = False
    get_password = password.get_password


def init(subcommand_parser):
    """Sets up the `profile` subcommand with `show` and `set` subcommands.
            `show` will print the current profile while `set` will modify profile properties.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser_profile = subcommand_parser.add_parser("profile")
    parser_profile.set_defaults(func=show_profile)
    profile_subparsers = parser_profile.add_subparsers()

    parser_for_show_command = profile_subparsers.add_parser("show")
    parser_for_set_command = profile_subparsers.add_parser("set")

    parser_for_show_command.set_defaults(func=show_profile)
    parser_for_set_command.set_defaults(func=set_profile)
    _add_args_to_set_command(parser_for_set_command)


def get_profile():
    # type: () -> Code42Profile
    """Returns the current profile object."""
    profile_values = config.get_config_profile()
    profile = Code42Profile()
    profile.authority_url = profile_values.get(ConfigurationKeys.AUTHORITY_KEY)
    profile.username = profile_values.get(ConfigurationKeys.USERNAME_KEY)
    profile.ignore_ssl_errors = profile_values.get(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)
    return profile


def show_profile(*args):
    """Prints the current profile to STDOUT."""
    profile = config.get_config_profile()
    print("\nProfile:")
    for key in profile:
        print("\t* {} = {}".format(key, profile[key]))

    # Don't prompt here because it may be confusing from a UX perspective
    if password.get_password(prompt_if_not_exists=False) is not None:
        print("\t* A password is set.")

    print("")


def set_profile(args):
    """Sets the current profile using command line arguments."""
    if not _verify_args_for_initial_profile_set(args):
        exit(1)
    elif not config.profile_has_been_set():
        config.mark_as_set()

    _try_set_authority_url(args)
    _try_set_username(args)
    _try_set_ignore_ssl_errors(args)
    _try_set_password(args)

    if args.show:
        show_profile()


def _add_args_to_set_command(parser_for_set_command):
    _add_authority_arg(parser_for_set_command)
    _add_username_arg(parser_for_set_command)
    _add_password_arg(parser_for_set_command)
    _add_disable_ssl_errors_arg(parser_for_set_command)
    _add_enable_ssl_errors_arg(parser_for_set_command)
    _add_show_arg(parser_for_set_command)


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
        help="The password for the Code42 API user. Passwords are not stored in plain text.",
    )


def _add_disable_ssl_errors_arg(parser):
    parser.add_argument(
        "--disable-ssl-errors",
        action="store_true",
        default=None,
        dest="disable_ssl_errors",
        help="Do not validate the SSL certificates of Code42 servers.",
    )


def _add_enable_ssl_errors_arg(parser):
    parser.add_argument(
        "--enable-ssl-errors",
        action="store_true",
        default=None,
        dest="enable_ssl_errors",
        help="Do validate the SSL certificates of Code42 servers.",
    )


def _add_show_arg(parser):
    parser.add_argument(
        "--show",
        action="store_true",
        dest="show",
        help="Whether to show the profile after setting it.",
    )


def _set_has_args(args):
    return args.c42_authority_url is not None or args.c42_username is not None


def _try_set_authority_url(args):
    if args.c42_authority_url is not None:
        config.set_authority_url(args.c42_authority_url)


def _try_set_username(args):
    if args.c42_username is not None:
        config.set_username(args.c42_username)


def _try_set_ignore_ssl_errors(args):
    if args.disable_ssl_errors is not None and not args.enable_ssl_errors:
        config.set_ignore_ssl_errors(True)

    if args.enable_ssl_errors is not None:
        config.set_ignore_ssl_errors(False)


def _try_set_password(args):
    if args.do_set_c42_password:
        password.set_password()

    # Prompt for password if it does not exist for the current username / authority host address combo.
    password.get_password()


def _verify_args_for_initial_profile_set(args):
    if not config.profile_has_been_set() and (
        args.c42_username is None or args.c42_authority_url is None
    ):
        if args.c42_username is None:
            print_error("Missing username argument.")
        if args.c42_authority_url is None:
            print_error("Missing Code42 Authority URL argument.")
        return False
    return True


if __name__ == "__main__":
    show_profile()
