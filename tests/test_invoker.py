import pytest

from requests.exceptions import HTTPError

from py42.exceptions import Py42ForbiddenError

from code42cli import PRODUCT_NAME
from code42cli.commands import Command
from code42cli.invoker import CommandInvoker
from code42cli.parser import ArgumentParserError, CommandParser


def dummy_method(one, two, three=None):
    if three == "test":
        return "success"


def load_subcommands(*args):
    return [
        Command("testsub1", "the subdesc1", subcommand_loader=load_sub_subcommands),
        Command("testsub2", "the subdesc2"),
    ]


def load_sub_subcommands():
    return [Command("inner1", "the innerdesc1", handler=dummy_method)]


@pytest.fixture
def mock_parser(mocker):
    return mocker.MagicMock(spec=CommandParser)


class TestCommandInvoker(object):
    def test_run_top_cmd(self, mock_parser):
        cmd = Command("", "top level desc", subcommand_loader=load_subcommands)
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run([])
        mock_parser.prepare_cli_help.assert_called_once_with(cmd)

    def test_run_nested_cmd_calls_prepare_command(self, mock_parser):
        cmd = Command("", "top level desc", subcommand_loader=load_subcommands)
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run(["testsub1", "inner1", "one", "two", "--three", "test"])
        subcommand = cmd.subcommands[0].subcommands[0]
        mock_parser.prepare_command.assert_called_once_with(subcommand, ["testsub1", "inner1"])

    def test_run_nested_cmd_calls_successfully(self, mocker, mock_parser):
        cmd = Command("", "top level desc", subcommand_loader=load_subcommands)
        parsed_args = mocker.MagicMock()
        mock_parser.parse_args.return_value = parsed_args
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run(["testsub1", "inner1", "one", "two", "--three", "test"])
        assert parsed_args.func.call_count

    def test_run_nested_cmd_when_raises_argumentparsererror_prints_help(self, mocker, mock_parser):
        cmd = Command("", "top level desc", subcommand_loader=load_subcommands)
        mock_parser.parse_args.side_effect = ArgumentParserError()
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)
        with pytest.raises(SystemExit):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
        assert mock_subparser.print_help.call_count

    def test_run_when_errors_occur_from_handler_calls_log_error(self, mocker, mock_parser):
        error_logger = mocker.patch("{}.invoker.log_error".format(PRODUCT_NAME))
        ex = Exception()
        cmd = Command("", "top level desc", subcommand_loader=load_subcommands)
        mock_parser.parse_args.side_effect = ex
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
        error_logger.assert_called_once_with(ex)

    def test_run_when_forbidden_error_occurs_prints_message(self, mocker, mock_parser, capsys):
        mocker.patch("{}.invoker.log_error".format(PRODUCT_NAME))
        http_error = mocker.MagicMock(spec=HTTPError)
        cmd = Command("", "top level desc", subcommand_loader=load_subcommands)
        mock_parser.parse_args.side_effect = Py42ForbiddenError(http_error)
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])

        capture = capsys.readouterr()
        assert (
            u"You do not have the necessary permissions to perform this task. Try using or "
            u"creating a different profile." in capture.out
        )
