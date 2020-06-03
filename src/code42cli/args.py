from collections import OrderedDict
import inspect


PROFILE_HELP = u"The name of the Code42 CLI profile to use when executing this command."
SDK_ARG_NAME = u"sdk"
PROFILE_ARG_NAME = u"profile"


class ArgConfig(object):
    """Stores a set of argparse commands for later use by a command."""

    def __init__(self, *args, **kwargs):
        self._settings = {
            u"action": kwargs.get(u"action"),
            u"choices": kwargs.get(u"choices"),
            u"default": kwargs.get(u"default"),
            u"help": kwargs.get(u"help"),
            u"options_list": list(args),
            u"nargs": kwargs.get(u"nargs"),
            u"metavar": kwargs.get(u"metavar"),
            u"required": kwargs.get(u"required"),
        }

    @property
    def settings(self):
        return self._settings

    def set_choices(self, choices):
        self._settings[u"choices"] = choices

    def set_help(self, help):
        self._settings[u"help"] = help

    def add_short_option_name(self, short_name):
        self._settings[u"options_list"].append(short_name)

    def as_multi_val_param(self, nargs=u"+"):
        self._settings[u"nargs"] = nargs

    def set_required(self, required):
        self._settings[u"required"] = required


class ArgConfigCollection(object):
    def __init__(self):
        self._arg_configs = OrderedDict()

    @property
    def arg_configs(self):
        return self._arg_configs

    def append(self, name, arg_config):
        self._arg_configs[name] = arg_config

    def extend(self, arg_config_dict):
        self.arg_configs.update(arg_config_dict)


def get_auto_arg_configs(handler):
    """Looks at the parameter names of `handler` and builds an `ArgConfigCollection` containing
    `argparse` parameters based on them."""
    arg_configs = ArgConfigCollection()
    excluded_args = [SDK_ARG_NAME, u"profile", u"args", u"kwargs", u"self"]
    if callable(handler):
        argspec = inspect.getargspec(handler)
        filtered_argspec = {
            key: position for position, key in enumerate(argspec.args) if key not in excluded_args
        }
        num_optional_args = len(argspec.defaults) if argspec.defaults else 0
        num_positional_args = len(argspec.args) - num_optional_args
        num_required_cli_args = len(filtered_argspec) - num_optional_args

        for key in filtered_argspec:
            arg_config = _create_auto_args_config(
                key, filtered_argspec[key], num_positional_args, num_required_cli_args, argspec
            )
            _set_smart_defaults(arg_config)
            arg_configs.append(key, arg_config)

        if SDK_ARG_NAME in argspec.args:
            _build_sdk_arg_configs(arg_configs)

    return arg_configs


def _create_auto_args_config(key, position, num_positional_args, num_required_cli_args, argspec):
    default = None
    required = None
    param_name = key.replace(u"_", u"-")
    last_positional_arg_idx = num_positional_args - 1
    option_names = [u"--{}".format(param_name)]
    # positional arguments will come first, so if the arg position
    # is greater than the index of the last positional arg, it's a kwarg.
    if position > last_positional_arg_idx:
        # this is a keyword arg, treat it as an optional cli arg.
        default_value = argspec.defaults[position - num_positional_args]
        default = default_value
    elif num_required_cli_args > 1:
        # this is a positional arg, treat it as a required cli arg.
        required = True
    else:
        option_names = [param_name]
    return ArgConfig(*option_names, default=default, required=required)


def _set_smart_defaults(arg_config):
    default = arg_config.settings.get(u"default")
    # make the param not require a value (e.g. --enable) if the default value of
    # the param is a bool.
    if type(default) == bool:
        arg_config.settings[u"action"] = u"store_{}".format(default).lower()


def _build_sdk_arg_configs(arg_config_collection):
    """Add extra cli parameters that will always be relevant when a handler needs the sdk."""
    profile = ArgConfig(u"--profile", help=PROFILE_HELP)
    debug = ArgConfig(u"-d", u"--debug", action=u"store_true", help=u"Turn on Debug logging.")
    extras = {PROFILE_ARG_NAME: profile, u"debug": debug}
    arg_config_collection.extend(extras)
