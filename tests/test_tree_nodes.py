from code42cli.tree_nodes import SubcommandNode
from code42cli.commands import Command


class TestSubcommandNode(object):
    def test_names_returns_names_of_commands(self):
        node = SubcommandNode("code42", [Command("foo", ""), Command("bar", "")])
        assert len(node.names) == 2
        assert "foo" in node.names
        assert "bar" in node.names

    # def test_getitem_when_item_is_arg_returns_arg_node(self):
    #
    #
    #     command = Command("foo", "", subcommand_loader=)
    #
    #     node = SubcommandNode("code42", [Command("foo", ""), Command("bar", "")])
