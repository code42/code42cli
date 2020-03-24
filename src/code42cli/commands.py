import inspect

from code42cli.args import ArgConfig, ArgConfigCollection, get_auto_arg_configs, PROFILE_HELP
from code42cli import profile as cliprofile
from code42cli.sdk_client import create_sdk


class DictObject(object):
    def __init__(self, _dict):
        self.__dict__ = _dict


class Command(object):
    def __init__(
        self,
        name,
        description,
        usage=None,
        handler=None,
        arg_customizer=None,
        subcommand_loader=None,
        use_single_arg_obj=None,
    ):
        self._name = name
        self._description = description
        self._usage = usage
        self._handler = handler
        self._arg_customizer = arg_customizer
        self._subcommand_loader = subcommand_loader
        self._use_single_arg_obj = use_single_arg_obj
        self._args = {}
        self._subcommands = []

    def __call__(self, *args, **kwargs):
        if callable(self._handler):
            kvps = _get_arg_kvps(args[0], self._handler)
            if self._use_single_arg_obj:
                kvps = _kvps_to_obj(kvps)
            return self._handler(**kvps)
        help_func = kwargs.pop(u"help_func", None)
        if help_func:
            return help_func()

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def usage(self):
        return self._usage

    @property
    def subcommands(self):
        return self._subcommands

    def load_subcommands(self):
        if callable(self._subcommand_loader):
            self._subcommands = self._subcommand_loader()

    def get_arg_configs(self):
        arg_config_collection = get_auto_arg_configs(self._handler)
        if callable(self._arg_customizer):
            self._arg_customizer(arg_config_collection)

        return arg_config_collection.arg_configs


def _get_arg_kvps(parsed_args, handler):
    # transform parsed args from argparse into a dict
    kvps = {}
    parsed_dict = parsed_args.__dict__
    for key in parsed_dict:
        kvps[key] = parsed_dict[key]
    kvps.pop(u"func", None)
    return _inject_params(kvps, handler)


def _inject_params(kvps, handler):
    if _handler_has_arg(u"sdk", handler):
        profile_name = kvps.pop(u"profile", None)
        debug = kvps.pop(u"debug", None)

        profile = cliprofile.get_profile(profile_name)
        kvps[u"sdk"] = create_sdk(profile, debug)

        if _handler_has_arg(u"profile", handler):
            kvps[u"profile"] = profile
    return kvps


def _handler_has_arg(arg_name, handler):
    argspec = inspect.getargspec(handler)
    return arg_name in argspec.args


def _kvps_to_obj(kvps):
    new_kvps = {key: kvps[key] for key in kvps if key in ["sdk", "profile"]}
    new_kvps[u"args"] = DictObject(kvps)
    return new_kvps
