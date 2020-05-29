import sys

import difflib

from py42.exceptions import Py42HTTPError, Py42ForbiddenError

from code42cli.compat import str
from code42cli.errors import Code42CLIError
from code42cli.parser import ArgumentParserError, CommandParser
from code42cli.logger import get_main_cli_logger

_DIFFLIB_CUT_OFF = 0.7


class CommandInvoker(object):

    _COMMAND_KEYWORDS = {}
    _COMMAND_ARG_KEYWORDS = {}

    def __init__(self, top_command, cmd_parser=None):
        self._top_command = top_command
        self._cmd_parser = cmd_parser or CommandParser()
        self._commands = {u"": self._top_command}

    def run(self, input_args):
        """Locates a command that matches the one specified by
        `input_args` and runs it with the supplied parameters.
        
        Args:
            input_args (iter[str]): the full list of arguments
            supplied by the user to `code42` cli command.
        """
        invocation_str = u"code42 {}".format(u" ".join(input_args))
        try:
            path_parts = self._get_path_parts(input_args)
            command = self._commands.get(u" ".join(path_parts))
            self._try_run_command(command, path_parts, input_args)
        except Code42CLIError as err:
            logger = get_main_cli_logger()
            logger.print_and_log_error(str(err))
        except Py42ForbiddenError as err:
            logger = get_main_cli_logger()
            logger.log_verbose_error(invocation_str, err.response.request)
            logger.print_and_log_permissions_error()
            logger.print_errors_occurred_message()
        except Py42HTTPError as err:
            logger = get_main_cli_logger()
            logger.log_verbose_error(invocation_str, err.response.request)
            logger.print_errors_occurred_message()
        except Exception:
            logger = get_main_cli_logger()
            logger.log_verbose_error(invocation_str)
            logger.print_errors_occurred_message()

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
            self._set_command_keywords(new_key)

    def _try_run_command(self, command, path_parts, input_args):
        """Runs a command called using `path_parts` by parsing
        `input_args` and calling the command's handler."""
        parser = None
        try:
            if not path_parts:
                parser = self._cmd_parser.prepare_cli_help(command)
            else:
                parser = self._cmd_parser.prepare_command(command, path_parts)
                self._set_argument_keywords(path_parts[0], command.get_arg_configs())
            parsed_args = self._cmd_parser.parse_args(input_args)
            parsed_args.func(parsed_args)
        except ArgumentParserError as err:
            logger = get_main_cli_logger()
            logger.print_and_log_error(u"{}".format(err))
            possible_correct_words = self._find_incorrect_word_match(err, path_parts)
            if possible_correct_words:
                logger.print_info(u"Did you mean one of the following?")
                for possible_correct_word in possible_correct_words:
                    logger.print_info(u"     {}".format(possible_correct_word))

            else:
                parser.print_help(sys.stderr)
            sys.exit(2)

    @staticmethod
    def _get_arg_flags(arguments):
        flag_names = []
        for arg in arguments.values():
            arg_flags = [name for name in arg.settings["options_list"] if name.startswith("-")]
            flag_names.extend(arg_flags)
        return flag_names

    def _set_argument_keywords(self, command_key, arguments):
        self._COMMAND_ARG_KEYWORDS[command_key] = set()
        self._COMMAND_ARG_KEYWORDS[command_key].update(CommandInvoker._get_arg_flags(arguments))

    def _set_command_keywords(self, new_key):
        """Creates a dictionary, with top level command as key and set of all its subcommands
        as values.
        """
        command_keys = new_key.split()
        if len(command_keys) == 1:
            self._COMMAND_KEYWORDS[command_keys[0]] = set()
        else:
            self._COMMAND_KEYWORDS[command_keys[0]].update(command_keys[1:])

    def _find_incorrect_word_match(self, error, path_parts):
        possible_correct_words = []

        try:
            # Here we assume the error string contains ":", for case where it doesn't we
            # assume the error is not due to misspelled word and we return error as is.
            error_detail, unmatched_words = str(error).split(u":")
        except ValueError:
            return possible_correct_words

        if not unmatched_words or error_detail != u"unrecognized arguments":
            return possible_correct_words

        # Arg-parser sets the first/leftmost incorrect command keyword in the error message.
        unmatched_word = unmatched_words.split()[0]

        if not path_parts:
            available_values = self._COMMAND_KEYWORDS.keys()
        elif unmatched_word.strip().startswith("-"):
            available_values = self._COMMAND_ARG_KEYWORDS[path_parts[0]]
        else:
            available_values = self._COMMAND_KEYWORDS[path_parts[0]]

        return difflib.get_close_matches(unmatched_word, available_values, cutoff=_DIFFLIB_CUT_OFF)
