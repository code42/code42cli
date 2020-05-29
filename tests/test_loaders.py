from code42cli.loaders import SubcommandLoader
from code42cli.commands import Command
from .conftest import TestSubcommandLoader


class TestCommandSubcommandLoader(object):
    def test_names_when_no_subcommands_returns_nothing(self):
        subcommand_loader = SubcommandLoader("")
        assert not subcommand_loader.names

    def test_names_returns_expected_names(self):
        subcommand_loader = SubcommandLoader("")
        subcommand_loader.load_commands = lambda: [
            Command("c1", ""),
            Command("c2", ""),
            Command("c3", ""),
        ]
        assert subcommand_loader.names == ["c1", "c2", "c3"]

    def test_getitem_returns_expected_subtree(self):
        subcommand_loader = SubcommandLoader("")
        subcommand_loader_sub = SubcommandLoader("sub")
        subcommand_loader_sub.load_commands = lambda: [
            Command("c1", ""),
            Command("c2", ""),
            Command("c3", ""),
        ]
        command = Command("c1", "", subcommand_loader=TestSubcommandLoader(""))
        subcommand_loader.load_commands = lambda: [command]
        assert subcommand_loader._subtrees
