from code42cli.tree_nodes import SubcommandNode, ArgNode, FileNameArgNode
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
        test = node["test"]
        actual = test["--two"].names
        assert choices == actual


class TestArgNode(object):
    def test_getitem_when_an_arg_has_choices_returns_choices_node(self):
        arg1 = ArgConfig("-t")
        arg2 = ArgConfig("-p")
        choices = ["choice1, choice2, choice3"]
        arg2.set_choices(choices)

        node = ArgNode({"arg1": arg1, "arg2": arg2})
        actual = node["-p"].names
        assert choices == actual

    def test_getitem_when_an_arg_is_filename_arg_returns_file_arg_node_type(self):
        arg1 = ArgConfig("filename")
        arg2 = ArgConfig("-p")
        node = ArgNode({"filename": arg1, "arg2": arg2})
        assert FileNameArgNode == type(node["filename"])

    def test_getitem_when_an_arg_is_file_name_arg_returns_file_arg_node_type(self):
        arg1 = ArgConfig("file-name")
        arg2 = ArgConfig("-p")
        node = ArgNode({"file-name": arg1, "arg2": arg2})
        assert FileNameArgNode == type(node["file-name"])

    def test_getitem_when_an_arg_is_marked_as_a_file_arg_returns_file_arg_node_type(self):
        arg1 = ArgConfig("-t")
        arg1.as_file_arg()
        arg2 = ArgConfig("-p")
        node = ArgNode({"-t": arg1, "arg2": arg2})
        assert FileNameArgNode == type(node["-t"])
