from code42cli.tree_nodes import SubcommandNode
from code42cli.commands import Command
from code42cli.args import ArgConfig

from .conftest import DummySubcommandLoader, func_single_positional_arg_many_optional_args


class TestSubcommandNode(object):
    def test_names_returns_names_of_commands(self):
        node = SubcommandNode("code42", [Command("foo", ""), Command("bar", "")])
        assert len(node.names) == 2
        assert "foo" in node.names
        assert "bar" in node.names

    def test_getitem_when_item_is_subcommand_returns_its_node_with_expected_names(self):
        loader = DummySubcommandLoader("test")
        command = Command("test", "", subcommand_loader=loader)
        node = SubcommandNode("code42", [Command("foo", ""), command])
        actual = node["test"].names
        # values found in TestSubcommandLoader
        assert "sub1" in actual
        assert "sub2" in actual
        assert "sub3" in actual

    def test_getitem_when_item_is_arg_node_returns_flagged_based_args(self):
        command = Command("test", "", handler=func_single_positional_arg_many_optional_args)
        node = SubcommandNode("code42", [Command("foo", ""), command])
        actual = node["test"].names
        # values found in func_single_positional_arg_many_optional_args
        assert "--two" in actual
        assert "--three" in actual
        assert "--four" in actual

    def test_getitem_when_item_is_arg_with_choices_returns_node_with_choices_for_names(self):
        choices = ["something", "another"]
        arg_config = ArgConfig("--two")
        arg_config.set_choices(choices)

        def _customize_arg(argument_collection):
            argument_collection.arg_configs["two"] = arg_config

        command = Command(
            "test",
            "",
            handler=func_single_positional_arg_many_optional_args,
            arg_customizer=_customize_arg,
        )
        node = SubcommandNode("code42", [Command("foo", ""), command])
        actual = node["test"]["--two"].names
        assert choices == actual
