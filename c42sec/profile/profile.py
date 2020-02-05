from getpass import getpass

import c42sec.profile._config as config
import c42sec.profile._password as password
from c42sec.profile._config import ConfigurationKeys
from c42sec.util import print_error


class C42SecProfile(object):
    authority_url = ""
    username = ""
    ignore_ssl_errors = False
    get_password = password.get_password


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
    profile_values = config.get_config_profile()
    profile = C42SecProfile()
    profile.authority_url = profile_values.get(ConfigurationKeys.AUTHORITY_KEY)
    profile.username = profile_values.get(ConfigurationKeys.USERNAME_KEY)

    config_ignore_ssl_errors = profile_values.get(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)
    profile.ignore_ssl_errors = config_ignore_ssl_errors == "True"
    return profile


def show_profile(*args):
    """Prints the current profile to stdout."""
    profile = config.get_config_profile()
    print("")
    print("Profile:")

    for key in profile:
        print("\t* {} = {}".format(key, profile[key]))

    if password.get_password() is not None:
        print("\t* A password exists for this profile.")

    print("")


def set_profile(args):
    """Sets the current profile using command line arguments."""
    if not _verify_args_for_initial_profile_set(args):
        exit(1)
    else:
        config.mark_as_set()

    _try_set_authority_url(args)
    _try_set_username(args)
    _try_set_ignore_ssl_errors(args)
    _try_set_password(args)

    if args.show:
        show_profile()


def _add_set_command_args(parser):
    _add_authority_arg(parser)
    _add_username_arg(parser)
    _add_password_arg(parser)
    _add_disable_ssl_errors_arg(parser)
    _add_enable_ssl_errors_arg(parser)
    _add_show_arg(parser)


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
        help="Do not validate the SSL certificates of Code42 servers.",
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
        print("'Code42 authority URL' updated.")


def _try_set_username(args):
    if args.c42_username is not None:
        config.set_username(args.c42_username)
        print("'Code42 username' updated.")


def _try_set_ignore_ssl_errors(args):
    if args.disable_ssl_errors is not None and not args.enable_ssl_errors:
        config.set_ignore_ssl_errors(True)
        print("'Ignore SSL errors' updated.")

    if args.enable_ssl_errors is not None:
        config.set_ignore_ssl_errors(False)
        print("'Ignore SSL errors' updated.")


def _try_set_password(args):
    # Must happen after setting username
    if args.do_set_c42_password or (password.get_password() is None and args.c42_username is not None):
        user_password = getpass()
        password.set_password(user_password)
        print("'Code42 Password' updated.")


def _verify_args_for_initial_profile_set(args):
    if not config.profile_has_been_set() and (args.c42_username is None or args.c42_authority_url is None):
        if args.c42_username is None:
            print_error("ERROR: Missing username argument.")

        if args.c42_authority_url is None:
            print_error("ERROR: Missing Code42 Authority URL argument.")

        return False

    return True


if __name__ == "__main__":
    show_profile()
