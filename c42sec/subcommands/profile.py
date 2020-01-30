from c42sec.common.util import get_user_project_path
from configparser import ConfigParser


_DEST_AUTHORITY_KEY = u"c42_authority_url"
_DEST_USERNAME_KEY = u"c42_username"
_ROOT_SECTION_NAME = u"Code42"


def init(c42sec_arg_parser):
    _init_config_file_if_not_exists()

    subparsers = c42sec_arg_parser.add_subparsers()
    parser_profile = subparsers.add_parser("profile")
    parser_profile.set_defaults(func=show)
    profile_subparsers = parser_profile.add_subparsers()

    parser_show = profile_subparsers.add_parser("show")
    parser_set = profile_subparsers.add_parser("set")

    parser_show.set_defaults(func=show)
    parser_set.set_defaults(func=set)
    _add_set_command_args(parser_set)


def show(*args):
    _init_config_file_if_not_exists()
    config_file_path = _get_config_file_path()
    config_parser = ConfigParser()
    config_parser.read(config_file_path)
    config_args = config_parser[_ROOT_SECTION_NAME]
    print()
    print("Current subcommands:")
    print("========================")
    for key in config_parser[_ROOT_SECTION_NAME]:
        print("{} = {}".format(key, config_args[key]))
    print()


def set(*args):
    print(args)


def _add_set_command_args(parser):
    _add_authority_arg(parser)
    _add_username_arg(parser)


def _add_authority_arg(parser):
    parser.add_argument(
        "-s",
        "--server",
        action="store",
        dest=_DEST_AUTHORITY_KEY,
        help="The full scheme, url and port of the Code42 server."
    )


def _add_username_arg(parser):
    parser.add_argument(
            "-u",
            "--username",
            action="store",
            dest=_DEST_USERNAME_KEY,
            help="The username of the Code42 API user.",
    )


def _init_config_file_if_not_exists():
    config_file_path = _get_config_file_path()
    try:
        open(config_file_path, "r").close()
    except IOError:
        _create_new_config_file()


def _get_config_file_path():
    return "{}/config.cfg".format(get_user_project_path())


def _create_new_config_file():
    config_parser = ConfigParser()
    config_parser[_ROOT_SECTION_NAME] = {}
    config_parser[_ROOT_SECTION_NAME][_DEST_AUTHORITY_KEY] = "null"
    config_parser[_ROOT_SECTION_NAME][_DEST_USERNAME_KEY] = "null"
    config_file_path = _get_config_file_path()
    with open(config_file_path, "w+") as config_file:
        config_parser.write(config_file)


if __name__ == "__main__":
    show()
