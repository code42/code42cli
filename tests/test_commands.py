import pytest
from py42.sdk import SDKClient

from code42cli import PRODUCT_NAME
from code42cli.args import ArgConfig, SDK_ARG_NAME, PROFILE_ARG_NAME
from code42cli.commands import Command, DictObject, SubcommandLoader
from code42cli.profile import Code42Profile
from .conftest import (
    func_keyword_args,
    func_mixed_args,
    func_positional_args,
    func_with_args,
    func_with_sdk,
    func_single_positional_arg_with_sdk_and_profile,
    func_single_positional_arg,
    func_single_positional_arg_many_optional_args,
    subcommand1,
    subcommand2,
    subcommand3,
    TestSubcommandLoader,
)


def arg_customizer(arg_collection):
    arg_collection.append("success", ArgConfig("--success"))


@pytest.fixture
def mock_profile_reader(mocker):
    return mocker.patch("{}.profile.get_profile".format(PRODUCT_NAME))


@pytest.fixture
def mock_sdk_client(mocker, mock_42):
    client = mocker.MagicMock(spec=SDKClient)
    mock_42.return_value = client
    return client


class TestCommand(object):
    def test_name(self):
        command = Command("test", "test desc", "test usage")
        assert command.name == "test"

    def test_description(self):
        command = Command("test", "test desc", "test usage")
        assert command.description == "test desc"

    def test_usage(self):
        command = Command("test", "test desc", "test usage")
        assert command.usage == "test usage"

    def test_load_subcommands_makes_subcommands_accessible(self):
        command = Command(
            "test", "test desc", "test usage", subcommand_loader=TestSubcommandLoader("test")
        )
        command.load_subcommands()
        assert len(command.subcommands) == 3
        assert subcommand1 in command.subcommands
        assert subcommand2 in command.subcommands
        assert subcommand3 in command.subcommands

    def test_load_subcommands_when_no_loader_does_nothing(self):
        command = Command("test", "test desc", "test usage")
        command.load_subcommands()
        assert not len(command.subcommands)

    def test_get_arg_configs_when_no_func_returns_empty_collection(self):
        command = Command("test", "test desc", "test usage")
        coll = command.get_arg_configs()
        assert not coll

    def test_get_arg_configs_calls_arg_customizer_if_present(self):
        command = Command("test", "test desc", "test usage", func_keyword_args, arg_customizer)
        coll = command.get_arg_configs()
        assert "success" in coll

    def test_get_arg_configs_when_keyword_args_returns_expected_collection(self):
        command = Command("test", "test desc", "test usage", func_keyword_args)
        coll = command.get_arg_configs()
        assert "--one" in coll["one"].settings["options_list"]
        assert "--two" in coll["two"].settings["options_list"]
        assert "--three" in coll["three"].settings["options_list"]
        assert "--default" in coll["default"].settings["options_list"]

    def test_get_arg_configs_when_keyword_args_has_defaults_set(self):
        command = Command("test", "test desc", "test usage", func_keyword_args)
        coll = command.get_arg_configs()
        assert coll["default"].settings["default"] == "testdefault"

    def test_get_arg_configs_when_positional_args_returns_expected_collection(self):
        command = Command("test", "test desc", "test usage", func_positional_args)
        coll = command.get_arg_configs()
        assert "--one" in coll["one"].settings["options_list"]
        assert "--two" in coll["two"].settings["options_list"]
        assert "--three" in coll["three"].settings["options_list"]

    def test_get_arg_configs_when_positional_args_returns_all_required_args(self):
        command = Command("test", "test desc", "test usage", func_positional_args)
        coll = command.get_arg_configs()
        assert coll["one"].settings["required"] == True
        assert coll["two"].settings["required"] == True
        assert coll["three"].settings["required"] == True

    def test_get_arg_configs_when_mixed_args_returns_expected_collection(self):
        command = Command("test", "test desc", "test usage", func_mixed_args)
        coll = command.get_arg_configs()
        assert "--one" in coll["one"].settings["options_list"]
        assert "--two" in coll["two"].settings["options_list"]
        assert "--three" in coll["three"].settings["options_list"]
        assert "--four" in coll["four"].settings["options_list"]

    def test_get_arg_configs_when_mixed_args_returns_positional_args_required(self):
        command = Command("test", "test desc", "test usage", func_mixed_args)
        coll = command.get_arg_configs()
        assert coll["one"].settings["required"] == True
        assert coll["two"].settings["required"] == True
        assert not coll["three"].settings["required"]
        assert not coll["four"].settings["required"]

    def test_get_arg_configs_when_handler_with_sdk_includes_profile_and_debug(self):
        command = Command("test", "test desc", "test usage", func_with_sdk)
        coll = command.get_arg_configs()
        assert "--one" in coll["one"].settings["options_list"]
        assert "--two" in coll["two"].settings["options_list"]
        assert "--three" in coll["three"].settings["options_list"]
        assert "--four" in coll["four"].settings["options_list"]
        assert "--profile" in coll[PROFILE_ARG_NAME].settings["options_list"]
        assert "--debug" in coll["debug"].settings["options_list"]
        assert not coll.get(SDK_ARG_NAME)

    def test_get_arg_configs_when_handler_with_args_excludes_args(self):
        command = Command("test", "test desc", "test usage", func_with_args)
        coll = command.get_arg_configs()
        assert not coll.get("args")

    def test_get_arg_configs_when_handler_has_single_positional_arg_and_sdk_and_profile_returns_expected_collection(
        self
    ):
        command = Command(
            "test", "test desc", "test usage", func_single_positional_arg_with_sdk_and_profile
        )
        coll = command.get_arg_configs()
        assert "one" in coll["one"].settings["options_list"]

    def test_get_arg_configs_when_handler_has_single_positional_arg_returns_expected_collection(
        self
    ):
        command = Command("test", "test desc", "test usage", func_single_positional_arg)
        coll = command.get_arg_configs()
        assert "one" in coll["one"].settings["options_list"]

    def test_get_arg_configs_when_handler_has_single_positional_arg_and_many_optional_args_returns_expected_collection(
        self
    ):
        command = Command(
            "test", "test desc", "test usage", func_single_positional_arg_many_optional_args
        )
        coll = command.get_arg_configs()
        assert "one" in coll["one"].settings["options_list"]
        assert "--two" in coll["two"].settings["options_list"]
        assert "--three" in coll["three"].settings["options_list"]
        assert "--four" in coll["four"].settings["options_list"]

    def test_get_arg_configs_when_handler_has_single_positional_arg_and_many_optional_args_optional_args_are_not_required(
        self
    ):
        command = Command(
            "test", "test desc", "test usage", func_single_positional_arg_many_optional_args
        )
        coll = command.get_arg_configs()
        assert not coll["two"].settings["required"]
        assert not coll["three"].settings["required"]
        assert not coll["four"].settings["required"]

    def test_call_when_keyword_args_passes_expected_values(self, mocker):
        def test_handler(one=None, two=None, three=None):
            if one == "testone" and two == "testtwo" and three == "testthree":
                return "success"

        command = Command("test", "test desc", "test usage", test_handler)
        kvps = {"one": "testone", "two": "testtwo", "three": "testthree"}
        kvps = DictObject(kvps)
        assert command(kvps) == "success"

    def test_call_when_positional_args_passes_expected_values(self, mocker):
        def test_handler(one, two, three):
            if one == "testone" and two == "testtwo" and three == "testthree":
                return "success"

        command = Command("test", "test desc", "test usage", test_handler)
        kvps = {"one": "testone", "two": "testtwo", "three": "testthree"}
        kvps = DictObject(kvps)
        assert command(kvps) == "success"

    def test_call_when_both_positional_and_optional_args_passes_expected_values(self, mocker):
        def test_handler(one, two, three=None, four=None):
            if (
                one == "testone"
                and two == "testtwo"
                and three == "testthree"
                and four == "testfour"
            ):
                return "success"

        command = Command("test", "test desc", "test usage", test_handler)
        kvps = {"one": "testone", "two": "testtwo", "three": "testthree", "four": "testfour"}
        kvps = DictObject(kvps)
        assert command(kvps) == "success"

    def test_call_when_handler_with_sdk_passes_expected_values(
        self, mocker, mock_sdk_client, mock_profile_reader
    ):
        def test_handler(sdk, one, two, three=None, four_underscore=None):
            if (
                sdk == mock_sdk_client
                and one == "testone"
                and two == "testtwo"
                and three == "testthree"
                and four_underscore == "testfour"
            ):
                return "success"

        command = Command("test", "test desc", "test usage", test_handler)
        kvps = {
            "one": "testone",
            "two": "testtwo",
            "three": "testthree",
            "four-underscore": "testfour",
        }
        kvps = DictObject(kvps)
        assert command(kvps) == "success"

    def test_call_when_handler_with_sdk_and_profile_passes_expected_values(
        self, mocker, mock_sdk_client, mock_profile_reader
    ):
        mock_profile = mocker.MagicMock(spec=Code42Profile)
        mock_profile_reader.return_value = mock_profile

        def test_handler(sdk, profile, one, two, three=None, four=None):
            if (
                sdk == mock_sdk_client
                and profile == mock_profile
                and one == "testone"
                and two == "testtwo"
                and three == "testthree"
                and four == "testfour"
            ):
                return "success"

        command = Command("test", "test desc", "test usage", test_handler)
        kvps = {"one": "testone", "two": "testtwo", "three": "testthree", "four": "testfour"}
        kvps = DictObject(kvps)
        assert command(kvps) == "success"

    def test_call_when_handler_with_args_calls_with_single_obj_with_expected_values(self):
        def test_handler(args):
            if args.one == "testone" and args.two == "testtwo" and args.three == "testthree":
                return "success"

        command = Command("test", "test desc", "test usage", test_handler, use_single_arg_obj=True)
        kvps = {"one": "testone", "two": "testtwo", "three": "testthree"}
        kvps = DictObject(kvps)
        assert command(kvps) == "success"

    def test_call_func_with_no_handler_and_print_help_prints_help(self):
        def dummy_print_help():
            return "success"

        command = Command("test", "test desc", "test usage")
        assert command(help_func=dummy_print_help) == "success"


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
        command = Command("c1", "", subcommand_loader=TestSubcommandLoader(""))
        subcommand_loader.load_commands = lambda: [command]
        assert subcommand_loader.names == ["c1"]
        assert subcommand_loader["c1"].names == ["sub1", "sub2", "sub3"]
