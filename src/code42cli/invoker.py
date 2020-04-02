from __future__ import print_function

import sys

from code42cli.parser import ArgumentParserError, CommandParser


class CommandInvoker(object):
    def __init__(self, top_command, cmd_parser=None):
        self._top_command = top_command
        self._cmd_parser = cmd_parser or CommandParser()
        self._commands = {}
        self._commands[u""] = self._top_command

    def run(self, input_args):
        path_parts = self._get_path_parts(input_args)
        command = self._commands.get(" ".join(path_parts))
        self._try_run_command(command, path_parts, input_args)

    def _get_path_parts(self, input_args):
        path = u""
        node = self._commands[u""]
        for arg in input_args:
            new_path = u"{} {}".format(path, arg).strip()
            self._load_subcommands(path, node)
            node = self._commands.get(new_path)
            if not node:
                break
            path = new_path
        return path.split()

    def _load_subcommands(self, path, node):
        node.load_subcommands()
        for command in node.subcommands:
            new_key = u"{} {}".format(path, command.name).strip()
            self._commands[new_key] = command

    def _try_run_command(self, command, path_parts, input_args):
        try:
            if not path_parts:
                parser = self._cmd_parser.prepare_cli_help(command)
            else:
                parser = self._cmd_parser.prepare_command(command, path_parts)
            parsed_args = self._cmd_parser.parse_args(input_args)
            parsed_args.func(parsed_args)
        except ArgumentParserError as e:
            print(u"error: {}".format(e), file=sys.stderr)
            parser.print_help(sys.stderr)
            sys.exit(2)
