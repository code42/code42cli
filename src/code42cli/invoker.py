from __future__ import print_function

import sys

from py42.exceptions import Py42ForbiddenError

from code42cli import MAIN_COMMAND
from code42cli.parser import ArgumentParserError, CommandParser
from code42cli.logger import get_main_cli_logger, get_exception_logger


class CommandInvoker(object):
    def __init__(self, top_command, cmd_parser=None):
        self._top_command = top_command
        self._cmd_parser = cmd_parser or CommandParser()
        self._commands = {u"": self._top_command}
        self._log = get_main_cli_logger()
        self._exception_log = get_exception_logger()

    def run(self, input_args):
        """Locates a command that matches the one specified by
        `input_args` and runs it with the supplied parameters.
        
        Args:
            input_args (iter[str]): the full list of arguments
            supplied by the user to `code42` cli command.
        """
        command = None
        try:
            path_parts = self._get_path_parts(input_args)
            command = self._commands.get(u" ".join(path_parts))
            command.invocation = u"{} {}".format(MAIN_COMMAND, u" ".join(input_args))
            self._try_run_command(command, path_parts, input_args)
        except Py42ForbiddenError as err:
            self._log.error(
                command,
                err,
                u"You do not have the necessary permissions to perform this task. "
                u"Try using or creating a different profile.",
            )

        except FileNotFoundError as err:
            self._log.error(command, err, u"File '{}' was not found.".format(err.filename))

        except Exception as err:
            self._log.log_error_to_log_file(command, err)

    def _get_path_parts(self, input_args):
        """Gets the portion of `input_args` that refers to a
        valid command or subcommand, removing parameters.
        For example, `input_args` of ["command", "sub", "--arg", "argval"]
        would return ["command", "sub"], assuming "command" is a top level command,
        "sub" is a subcommand of "command", and the rest of the values are normal parameters.
        Returns an empty string if a valid command or subcommand is not found.
        """
        path = u""
        node = self._commands[u""]
        # step through each segment of input_args until we find
        # something that _isn't_ a command or subcommand.
        for arg in input_args:
            new_path = u"{} {}".format(path, arg).strip()
            self._load_subcommands(path, node)
            node = self._commands.get(new_path)
            if not node:
                break
            path = new_path
        return path.split()

    def _load_subcommands(self, path, node):
        """Discovers a command's subcommands and registers them
        to the available list of commands for this Invoker."""
        node.load_subcommands()
        for command in node.subcommands:
            new_key = u"{} {}".format(path, command.name).strip()
            self._commands[new_key] = command

    def _try_run_command(self, command, path_parts, input_args):
        """Runs a command called using `path_parts` by parsing
        `input_args` and calling the command's handler."""
        parser = None
        try:
            if not path_parts:
                parser = self._cmd_parser.prepare_cli_help(command)
            else:
                parser = self._cmd_parser.prepare_command(command, path_parts)
            parsed_args = self._cmd_parser.parse_args(input_args)
            parsed_args.func(parsed_args)
        except ArgumentParserError as e:
            self._log.error(str(e))
            parser.print_help(sys.stderr)
            sys.exit(2)
