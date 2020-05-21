import pytest

from requests.exceptions import HTTPError
from requests import Response, Request
import logging

from py42.exceptions import Py42ForbiddenError

from code42cli.commands import Command, CommandController
from code42cli.errors import Code42CLIError
from code42cli.invoker import CommandInvoker
from code42cli.parser import ArgumentParserError, CommandParser


def dummy_method(one, two, three=None):
    if three == "test":
        return "success"


class SubcommandControllerTop(CommandController):
    def load_commands(self):
        return [
            Command("testsub1", "the subdesc1", controller=SubcommandControllerBottom("testsub1")),
            Command("testsub2", "the subdesc2"),
        ]


class SubcommandControllerBottom(CommandController):
    def load_commands(self):
        return [Command("inner1", "the innerdesc1", handler=dummy_method)]


def load_sub_subcommands():
    return [Command("inner1", "the innerdesc1", handler=dummy_method)]


@pytest.fixture
def mock_parser(mocker):
    return mocker.MagicMock(spec=CommandParser)


class TestCommandInvoker(object):
    def test_run_top_cmd(self, mock_parser):
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run([])
        mock_parser.prepare_cli_help.assert_called_once_with(cmd)

    def test_run_nested_cmd_calls_prepare_command(self, mock_parser):
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run(["testsub1", "inner1", "one", "two", "--three", "test"])
        subcommand = cmd.subcommands[0].subcommands[0]
        mock_parser.prepare_command.assert_called_once_with(subcommand, ["testsub1", "inner1"])

    def test_run_nested_cmd_calls_successfully(self, mocker, mock_parser):
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        parsed_args = mocker.MagicMock()
        mock_parser.parse_args.return_value = parsed_args
        invoker = CommandInvoker(cmd, mock_parser)
        invoker.run(["testsub1", "inner1", "one", "two", "--three", "test"])
        assert parsed_args.func.call_count

    def test_run_nested_cmd_when_raises_argumentparsererror_prints_help(self, mocker, mock_parser):
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = ArgumentParserError()
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)
        with pytest.raises(SystemExit):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
        assert mock_subparser.print_help.call_count

    def test_run_when_errors_occur_from_handler_calls_logs_error(self, mocker, mock_parser, caplog):
        ex = Exception("test")
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = ex
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)
        with caplog.at_level(logging.ERROR):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
            assert str(ex) in caplog.text

    def test_run_when_errors_occur_from_handler_calls_logs_command(
        self, mocker, mock_parser, caplog
    ):
        ex = Exception("test")
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = ex
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)
        with caplog.at_level(logging.ERROR):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
            assert "code42 testsub1 inner1 one two --invalid test" in caplog.text

    def test_run_when_forbidden_error_occurs_logs_message(self, mocker, mock_parser, caplog):
        http_error = mocker.MagicMock(spec=HTTPError)
        http_error.response = mocker.MagicMock(spec=Response)
        http_error.response.request = None
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = Py42ForbiddenError(http_error)
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)

        with caplog.at_level(logging.ERROR):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
            assert (
                u"You do not have the necessary permissions to perform this task. Try using or "
                u"creating a different profile." in caplog.text
            )

    def test_run_when_forbidden_error_occurs_logs_command(self, mocker, mock_parser, caplog):
        http_error = mocker.MagicMock(spec=HTTPError)
        http_error.response = mocker.MagicMock(spec=Response)
        http_error.response.request = None
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = Py42ForbiddenError(http_error)
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)

        with caplog.at_level(logging.ERROR):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
            assert "code42 testsub1 inner1 one two --invalid test" in caplog.text

    def test_run_when_forbidden_error_occurs_logs_request(self, mocker, mock_parser, caplog):
        http_error = mocker.MagicMock(spec=HTTPError)
        http_error.response = mocker.MagicMock(spec=Response)
        request = mocker.MagicMock(spec=Request)
        request.body = {"foo": "bar"}
        http_error.response.request = request
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = Py42ForbiddenError(http_error)
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)

        with caplog.at_level(logging.ERROR):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
            assert str(request.body) in caplog.text

    def test_run_when_cli_error_occurs_logs_request(self, mocker, mock_parser, caplog):
        cmd = Command("", "top level desc", controller=SubcommandControllerTop(""))
        mock_parser.parse_args.side_effect = Code42CLIError("a code42cli error")
        mock_subparser = mocker.MagicMock()
        mock_parser.prepare_command.return_value = mock_subparser
        invoker = CommandInvoker(cmd, mock_parser)

        with caplog.at_level(logging.ERROR):
            invoker.run(["testsub1", "inner1", "one", "two", "--invalid", "test"])
            assert "a code42cli error" in caplog.text
