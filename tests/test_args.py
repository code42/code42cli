from code42cli.args import ArgConfig, ArgConfigCollection, get_auto_arg_configs
from .conftest import (
    func_keyword_args,
    func_mixed_args,
    func_positional_args,
    func_with_args,
    func_with_sdk,
)


class TestArgConfig(object):
    def test_param_names_accessible_on_options_list(self):
        arg_config = ArgConfig("-t", "--test")
        names = arg_config.settings["options_list"]
        assert len(names) == 2
        assert names[0] == "-t"
        assert names[1] == "--test"

    def test_action_accessible(self):
        arg_config = ArgConfig("-t", "--test", action="store")
        assert arg_config.settings["action"] == "store"

    def test_choices_accessible(self):
        choices = ["one", "two"]
        arg_config = ArgConfig("-t", "--test", choices=choices)
        assert arg_config.settings["choices"] == choices

    def test_default_accessible(self):
        default = "testdefault"
        arg_config = ArgConfig("-t", "--test", default=default)
        assert arg_config.settings["default"] == default

    def test_help_accessible(self):
        help = "testhelp"
        arg_config = ArgConfig("-t", "--test", help=help)
        assert arg_config.settings["help"] == help

    def test_nargs_accessible(self):
        nargs = "+"
        arg_config = ArgConfig("-t", "--test", nargs=nargs)
        assert arg_config.settings["nargs"] == nargs

    def test_set_choices_modifies_choices(self):
        choices = ["something", "another"]
        arg_config = ArgConfig("-t", "--test")
        arg_config.set_choices(choices)
        assert arg_config.settings["choices"] == choices

    def test_set_help_modifies_help(self):
        help = "testhelp"
        arg_config = ArgConfig("-t", "--test")
        arg_config.set_help(help)
        assert arg_config.settings["help"] == help

    def test_add_short_option_name_modifies_options_list(self):
        arg_config = ArgConfig("--test")
        arg_config.add_short_option_name("-x")
        assert "-x" in arg_config.settings["options_list"]


class TestArgConfigCollection(object):
    def test_add_adds_arg_config(self):
        arg_config = ArgConfig()
        coll = ArgConfigCollection()
        coll.add("test", arg_config)
        assert coll.arg_configs["test"] == arg_config

    def test_extends_adds_multiple_arg_configs(self):
        configs = {}
        arg_config1 = ArgConfig()
        arg_config2 = ArgConfig()
        configs["one"] = arg_config1
        configs["two"] = arg_config2

        coll = ArgConfigCollection()
        coll.extend(configs)
        assert len(coll.arg_configs) == 2
        assert coll.arg_configs["one"] == arg_config1
        assert coll.arg_configs["two"] == arg_config2


def test_get_auto_arg_configs_when_func_with_args_excludes_args():
    pass
