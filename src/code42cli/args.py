import inspect

PROFILE_HELP = u"The name of the Code42 profile to be used when executing this command."


class ArgConfig(object):
    """Allows for reuse of args with similar options."""

    def __init__(self, *args, **kwargs):
        self._settings = {}
        self._settings[u"action"] = kwargs.get(u"action")
        self._settings[u"choices"] = kwargs.get(u"choices")
        self._settings[u"default"] = kwargs.get(u"default")
        self._settings[u"help"] = kwargs.get(u"help")
        self._settings[u"options_list"] = list(args)
        self._settings[u"nargs"] = kwargs.get(u"nargs")

    @property
    def settings(self):
        return self._settings

    def set_choices(self, choices):
        self._settings[u"choices"] = choices

    def set_help(self, help):
        self._settings[u"help"] = help

    def add_short_option_name(self, short_name):
        self._settings[u"options_list"].append(short_name)


class ArgConfigCollection(object):
    def __init__(self):
        self._arg_configs = {}

    @property
    def arg_configs(self):
        return self._arg_configs

    def append(self, name, arg_config):
        self._arg_configs[name] = arg_config

    def extend(self, arg_config_dict):
        for key in arg_config_dict:
            arg_config = arg_config_dict[key]
            self._arg_configs[key] = arg_config


def get_auto_arg_configs(handler):
    arg_configs = ArgConfigCollection()
    if callable(handler):
        argspec = inspect.getargspec(handler)
        num_args = len(argspec.args)
        num_kw_args = len(argspec.defaults) if argspec.defaults else 0

        for arg_position, key in enumerate(argspec.args):
            if not key in [u"sdk", u"args"]:
                arg_config = _create_auto_args_config(
                    arg_position, key, argspec, num_args, num_kw_args
                )
                _set_smart_defaults(arg_config)
                arg_configs.append(key, arg_config)

        if u"sdk" in argspec.args:
            _build_sdk_arg_configs(arg_configs)

    return arg_configs


def _create_auto_args_config(arg_position, key, argspec, num_args, num_kw_args):
    default = None
    param_name = key.replace(u"_", u"-")
    difference = num_args - num_kw_args
    if arg_position > difference - 1:
        # this is an optional arg
        default_value = argspec.defaults[arg_position - difference]
        option_names = [u"--{}".format(param_name)]
        default = default_value
    else:
        # required (positional) arg
        option_names = [param_name]
    return ArgConfig(*option_names, default=default)


def _set_smart_defaults(arg_config):
    default = arg_config.settings.get(u"default")
    nargs = u"+" if type(default) == list else None
    arg_config.settings[u"nargs"] = nargs
    if type(default) == bool:
        arg_config.settings[u"action"] = u"store_{}".format(default).lower()


def _build_sdk_arg_configs(arg_config_collection):
    profile = ArgConfig(u"--profile", help=PROFILE_HELP)
    debug = ArgConfig(u"-d", u"--debug", action=u"store_true", help=u"Turn on Debug logging.")
    extras = {u"profile": profile, u"debug": debug}
    arg_config_collection.extend(extras)
