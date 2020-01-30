import keyring
from c42sec.util import get_user_project_path, SERVICE_NAME
from configparser import ConfigParser


_SECTION = u"Code42"
_AUTHORITY_KEY = u"c42_authority_url"
_USERNAME_KEY = u"c42_username"
_PASSWORD_KEY = u"c42_password"
_IGNORE_SSL_ERRORS_KEY = u"ignore_ssl_errors"


def init(c42sec_arg_parser):
    subparsers = c42sec_arg_parser.add_subparsers()
    parser_profile = subparsers.add_parser("profile")
    parser_profile.set_defaults(func=show_profile)
    profile_subparsers = parser_profile.add_subparsers()

    parser_show = profile_subparsers.add_parser("show")
    parser_set = profile_subparsers.add_parser("set")

    parser_show.set_defaults(func=show_profile)
    parser_set.set_defaults(func=set_profile)
    _add_set_command_args(parser_set)


def get_profile():
    profile = _get_config_profile()
    password = _get_password(profile[_USERNAME_KEY])
    profile[_PASSWORD_KEY] = password
    return profile


def show_profile(*args):
    profile = _get_config_profile()

    print()
    print("Current profile:")
    print("========================")
    for key in profile:
        print("{} = {}".format(key, profile[key]))

    if _get_password(profile[_USERNAME_KEY]) is not None:
        print("Password is set.")

    print()


def set_profile(args):
    path = _get_config_file_path()
    parser = ConfigParser()
    profile = _get_config_profile_from_parser(parser)

    if args.c42_authority_url is not None:
        profile[_AUTHORITY_KEY] = args.c42_authority_url
        print("'Code42 authority URL' saved. New value: {}".format(args.c42_authority_url))

    if args.c42_username is not None:
        profile[_USERNAME_KEY] = args.c42_username
        print("'Code42 username' saved. New value: {}".format(args.c42_username))

    if args.ignore_ssl_errors is not None:
        profile[_IGNORE_SSL_ERRORS_KEY] = str(args.ignore_ssl_errors)
        print("'Ignore SSL errors' saved. New value: {}".format(args.ignore_ssl_errors))

    if args.c42_password is not None:
        keyring.set_password(SERVICE_NAME, _PASSWORD_KEY, args.c42_password)
        print("'Code42 Password' saved.")

    with open(path, "w+") as config_file:
        parser.write(config_file)


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
        dest=_AUTHORITY_KEY,
        help="The full scheme, url and port of the Code42 server."
    )


def _add_username_arg(parser):
    parser.add_argument(
            "-u",
            "--username",
            action="store",
            dest=_USERNAME_KEY,
            help="The username of the Code42 API user.",
    )


def _add_password_arg(parser):
    parser.add_argument(
        "-p",
        "--password",
        action="store",
        dest=_PASSWORD_KEY,
        help="The password for the Code42 API user. "
             "Note: if you don't supply a password, you will be prompted. "
             "Passwords are not stored in plain text."
    )


def _add_ignore_ssl_errors_arg(parser):
    parser.add_argument(
            "--ignore-ssl-errors",
            action="store_true",
            default=False,
            dest=_IGNORE_SSL_ERRORS_KEY,
            help="Do not validate the SSL certificates of Code42 servers",
    )


def _get_config_file_path():
    path = "{}/config.cfg".format(get_user_project_path())
    try:
        # Make sure exists
        open(path, "r").close()
    except IOError:
        _create_new_config_file()

    return path


def _get_config_profile():
    parser = ConfigParser()
    return _get_config_profile_from_parser(parser)


def _get_config_profile_from_parser(parser):
    config_file_path = _get_config_file_path()
    parser.read(config_file_path)
    return parser[_SECTION]


def _create_new_config_file():
    config_parser = ConfigParser()
    config_parser[_SECTION] = {}
    config_parser[_SECTION][_AUTHORITY_KEY] = "null"
    config_parser[_SECTION][_USERNAME_KEY] = "null"
    config_parser[_SECTION][_IGNORE_SSL_ERRORS_KEY] = False
    config_file_path = _get_config_file_path()
    with open(config_file_path, "w+") as config_file:
        config_parser.write(config_file)


def _get_password(username):
    return keyring.get_password(SERVICE_NAME, username)


if __name__ == "__main__":
    show_profile()
