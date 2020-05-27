import argparse
from argparse import RawDescriptionHelpFormatter, SUPPRESS

from py42.__version__ import __version__ as py42version

from code42cli.__version__ import __version__ as cliversion

BANNER = u""" 
 dP""b8  dP"Yb  8888b. 888888  dP88  oP"Yb. 
dP   `" dP   Yb 8I  Yb 88__   dP 88  "' dP' 
Yb      Yb   dP 8I  dY 88""  d888888   dP'  
 YboodP  YbodP  8888Y" 888888    88  .d8888
 
code42cli version {}, by Code42 Software.
powered by py42 version {}.""".format(
    cliversion, py42version
)


class ArgumentParserError(Exception):
    pass


class CommandParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        # noinspection PyTypeChecker
        super(CommandParser, self).__init__(
            formatter_class=RawDescriptionHelpFormatter, add_help=False, **kwargs
        )
        self.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )

    def prepare_command(self, command, path_parts):
        parser = self._get_parser(command, path_parts)
        self._load_argparse_config(command, parser)
        parser.set_defaults(func=lambda args: command(args, help_func=parser.print_help))
        return parser

    def prepare_cli_help(self, top_command):
        top_command.load_subcommands()
        self.description = _get_group_help(top_command)
        self.usage = SUPPRESS
        self.set_defaults(func=lambda _: self.print_help())
        return self

    def error(self, message):
        # overrides the behavior of when an error occurs when
        # arguments can't be successfully parsed. CommandInvoker catches this.
        raise ArgumentParserError(message)

    def _load_argparse_config(self, command, command_parser):
        arg_configs = command.get_arg_configs()
        required_group = command_parser.add_argument_group(u"required arguments")
        for arg in arg_configs:
            _add_argument(command_parser, arg_configs[arg].settings, required_group)

    def _get_parser(self, command, path_parts):
        usage = command.usage or SUPPRESS
        command.load_subcommands()
        description = _get_group_help(command) if command.subcommands else command.description
        subparser = self._get_subparser(path_parts)
        return subparser.add_parser(command.name, description=description, usage=usage)

    def _get_subparser(self, path_parts):
        global_subparser = self.add_subparsers()
        global_subparser.required = True
        subparsers = {(): global_subparser}
        parent_subparser = global_subparser

        # build out the entire path of subparsers up to the command
        for part in range(0, len(path_parts)):
            parent_path_parts = tuple(path_parts[:part])
            parent_subparser = subparsers.get(parent_path_parts)
            if not parent_subparser:
                parent_subparser = _get_parent_subparser(path_parts, part, subparsers)
            subparsers[parent_path_parts] = parent_subparser
        return parent_subparser


def _get_parent_subparser(path_parts, part, subparsers):
    grandparent_path_parts = tuple(path_parts[: part - 1])
    grandparent_subparser = subparsers[grandparent_path_parts]

    new_path = path_parts[part - 1]
    new_parser = grandparent_subparser.add_parser(new_path)
    parent_subparser = new_parser.add_subparsers()
    parent_subparser.required = True

    return parent_subparser


def _add_argument(parser, arg_settings, required_group):
    # register the settings of an ArgConfig object to an argparse parser
    options_list = arg_settings.pop(u"options_list")
    arg_settings = {key: arg_settings[key] for key in arg_settings if arg_settings[key] is not None}
    if arg_settings.get(u"required"):
        parser = required_group
    parser.add_argument(*options_list, **arg_settings)


def _get_group_help(command):
    descriptions = _build_group_command_descriptions(command)
    output = []
    name = command.name
    if not name:
        name = u"code42"
        output.append(BANNER)

    output.extend([u" \nAvailable commands in <{}>:".format(name), descriptions])
    return u"\n".join(output)


def _build_group_command_descriptions(command):
    subs = command.subcommands
    name_width = len(max([cmd.name for cmd in subs], key=len))
    lines = [u"  {} - {}".format(cmd.name.ljust(name_width), cmd.description) for cmd in subs]
    return u"\n".join(lines)
