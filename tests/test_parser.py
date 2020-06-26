import pytest

from code42cli.commands import Command, SubcommandLoader
from code42cli.parser import (
    ArgumentParserError,
    CommandParser,
    exit_if_mutually_exclusive_args_used_together,
)

import code42cli.cmds.search_shared.enums as enums


def dummy_method():
    return "success"


def dummy_method_required_args(one, two):
    return "success"


def dummy_method_optional_args(one=None, two=None):
    if one == "onetest" and two == "twotest":
        return "success"


class MockSubcommandLoader(SubcommandLoader):
    def load_commands(self):
        return [Command("testsub1", "the subdesc1"), Command("testsub2", "the subdesc2")]


class TestCommandParser(object):
    def test_prepare_command_when_no_args(self):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        parsed_args = parser.parse_args(["runnable"])
        assert parsed_args.func(parsed_args) == "success"

    def test_prepare_command_when_no_args_and_nested(self):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method)
        parts = ["subgroup", "runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        parsed_args = parser.parse_args(["subgroup", "runnable"])
        assert parsed_args.func(parsed_args) == "success"

    def test_prepare_command_when_required_args(self):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method_required_args)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        parsed_args = parser.parse_args(["runnable", "--one", "onetest", "--two", "twotest"])
        assert parsed_args.func(parsed_args) == "success"

    def test_prepare_command_when_required_args_help_outputs_help(self, capsys):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method_required_args)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        success = False
        try:
            parser.parse_args(["runnable", "-h"])
        except SystemExit:
            success = True
            captured = capsys.readouterr()
            assert "the desc" in captured.out
            assert "one" in captured.out
            assert "two" in captured.out
        assert success

    def test_prepare_command_when_optional_args(self):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method_optional_args)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        parsed_args = parser.parse_args(["runnable", "--one", "onetest", "--two", "twotest"])
        assert parsed_args.func(parsed_args) == "success"

    def test_prepare_command_when_optional_args_help_outputs_help(self, capsys):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method_optional_args)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        success = False
        try:
            parsed_args = parser.parse_args(["runnable", "-h"])
        except SystemExit:
            success = True
            captured = capsys.readouterr()
            assert "the desc" in captured.out
            assert "--one" in captured.out
            assert "--two" in captured.out
        assert success

    def test_prepare_command_when_required_args_and_args_missing_throws(self, capsys):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method_required_args)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        with pytest.raises(ArgumentParserError):
            parsed_args = parser.parse_args(["runnable"])

    def test_prepare_command_when_extra_args_throws(self):
        cmd = Command("runnable", "the desc", "the usage", handler=dummy_method_optional_args)
        parts = ["runnable"]
        parser = CommandParser()
        parser.prepare_command(cmd, parts)
        with pytest.raises(ArgumentParserError):
            parsed_args = parser.parse_args(["runnable", "--invalid"])

    def test_prepare_cli_help_outputs_group_info(self, capsys):
        cmd = Command(
            "runnable", "the desc", "the usage", subcommand_loader=MockSubcommandLoader("runnable")
        )
        parser = CommandParser()
        parser.prepare_cli_help(cmd)
        parser.parse_args([])
        parser.print_help()
        captured = capsys.readouterr()
        assert "the subdesc1" in captured.out
        assert "testsub1" in captured.out
        assert "the subdesc2" in captured.out
        assert "testsub2" in captured.out


@pytest.mark.parametrize(
    "arg",
    [
        "c42_username",
        "actor",
        "md5",
        "sha256",
        "source",
        "file_name",
        "file_path",
        "process_owner",
        "tab_url",
    ],
)
def test_exit_if_advanced_query_used_with_other_search_args_when_is_advanced_query_and_other_incompatible_multi_narg_argument_passed(
    file_event_namespace, arg
):
    file_event_namespace.advanced_query = "some complex json"
    setattr(file_event_namespace, arg, ["test_value"])
    with pytest.raises(SystemExit):
        exit_if_mutually_exclusive_args_used_together(
            file_event_namespace, list(enums.FileEventFilterArguments())
        )


def test_exit_if_advanced_query_used_with_other_search_args_when_is_advanced_query_and_has_incremental_mode_does_not_exit_as_invalid_args_does_not_contain_incremental(alert_namespace):
    alert_namespace.advanced_query = "some complex json"
    alert_namespace.incremental = True
    exit_if_mutually_exclusive_args_used_together(
        alert_namespace, list(enums.AlertFilterArguments())
    )


def test_exit_if_advanced_query_used_with_other_search_args_when_is_advanced_query_and_has_include_non_exposure_exits(file_event_namespace):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.include_non_exposure = True
    with pytest.raises(SystemExit):
        exit_if_mutually_exclusive_args_used_together(
            file_event_namespace, list(enums.FileEventFilterArguments())
        )


def test_exit_if_advanced_query_used_with_other_search_args_when_is_advanced_query_and_has_format_does_not_exit(file_event_namespace):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.format = "JSON"
    exit_if_mutually_exclusive_args_used_together(
        file_event_namespace, list(enums.FileEventFilterArguments())
    )
