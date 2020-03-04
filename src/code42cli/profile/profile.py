from __future__ import print_function

import code42cli.profile.config as config
import code42cli.profile.password as password
from code42cli.profile.config import ConfigurationKeys
from code42cli.util import get_input


class Code42Profile(object):
    authority_url = u""
    username = u""
    ignore_ssl_errors = False

    @staticmethod
    def get_password():
        pwd = password.get_password()
        if not pwd:
            pwd = password.get_password_from_prompt()
        return pwd


def init(subcommand_parser):
    """Sets up the `profile` subcommand with `show` and `set` subcommands.
            `show` will print the current profile while `set` will modify profile properties.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser_profile = subcommand_parser.add_parser(u"profile")
    parser_profile.set_defaults(func=show_profile)
    profile_subparsers = parser_profile.add_subparsers()

    parser_for_show_command = profile_subparsers.add_parser(u"show")
    parser_for_set_command = profile_subparsers.add_parser(u"set")
    parser_for_reset_password = profile_subparsers.add_parser(u"reset-pw")

    parser_for_show_command.set_defaults(func=show_profile)
    parser_for_set_command.set_defaults(func=set_profile)
    parser_for_reset_password.set_defaults(func=prompt_for_password_reset)
    _add_args_to_set_command(parser_for_set_command)


def get_profile():
    """Returns the current profile object."""
    profile_values = config.get_config_profile()
    profile = Code42Profile()
    profile.authority_url = profile_values.get(ConfigurationKeys.AUTHORITY_KEY)
    profile.username = profile_values.get(ConfigurationKeys.USERNAME_KEY)
    profile.ignore_ssl_errors = profile_values.get(ConfigurationKeys.IGNORE_SSL_ERRORS_KEY)
    return profile


def show_profile(*args):
    """Prints the current profile to stdout."""
    profile = config.get_config_profile()
    print(u"\nProfile:")
    for key in profile:
        print(u"\t* {} = {}".format(key, profile[key]))

    if password.get_password() is not None:
        print(u"\t* A password is set.")
    print(u"")


def set_profile(args):
    """Sets the current profile using command line arguments."""
    _try_set_authority_url(args)
    _try_set_username(args)
    _try_set_ignore_ssl_errors(args)
    config.mark_as_set_if_complete()
    _prompt_for_allow_password_set()


def prompt_for_password_reset(*args):
    """Securely prompts for your password and then stores it using keyring."""
    password.set_password_from_prompt()


def _add_args_to_set_command(parser_for_set_command):
    _add_authority_arg(parser_for_set_command)
    _add_username_arg(parser_for_set_command)
    _add_disable_ssl_errors_arg(parser_for_set_command)
    _add_enable_ssl_errors_arg(parser_for_set_command)


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


def _prompt_for_allow_password_set():
    answer = get_input(u"Would you like to set a password? (y/n): ")
    if answer.lower() == u"y":
        prompt_for_password_reset()


if __name__ == "__main__":
    show_profile()
