import inspect

from code42cli import profile as cliprofile
from code42cli.args import get_auto_arg_configs, SDK_ARG_NAME, PROFILE_ARG_NAME
from code42cli.sdk_client import create_sdk


class DictObject(object):
    def __init__(self, _dict):
        self.__dict__ = _dict


class Command(object):
    """Represents a function that a CLI user can execute. Add a command to
    `code42cli.main._load_top_commands` or as a subcommand of one those
    commands to make it available for use.

    Args:
        name (str or unicode): The name of the command. For example, in
            `code42 profile show`, "show" is the name, while "profile"
            is the name of the parent command.

        description (str or unicode): Descriptive text to be displayed when using -h.

        usage (str or unicode, optional): A usage example to be displayed when using -h.
        handler (function, optional): The function to be exectued when the command is run.

        arg_customizer (function, optional): A function accepting a single `ArgCollection`
            parameter that allows for editing the collection when `get_arg_configs` is run.

        subcommand_loader (SubcommandLoader, optional): An object that can load subcommands 
            for this command.

        use_single_arg_obj (bool, optional): When True, causes all parameters sent to
            `__call__` to be consolidated in an object with attribute names dictated
            by the parameter names. That object is passed to `handler`'s `arg` parameter.
    """

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
        self._subcommands = []

    def __call__(self, *args, **kwargs):
        """Passes the parsed argparse args to the handler, or
        shows the help of for this command if there is no handler
        (common in commands that are simply groups of subcommands).
        """
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

    @property
    def subcommand_loader(self):
        return self._subcommand_loader

    def load_subcommands(self):
        self._subcommands = (
            self._subcommand_loader.load_commands() if self._subcommand_loader else []
        )
        return self._subcommands

    def get_arg_configs(self):
        """Returns a collection of argparse configurations based on
        the parameter names of `handler` and any user customizations."""
        arg_config_collection = get_auto_arg_configs(self._handler)
        if callable(self._arg_customizer):
            self._arg_customizer(arg_config_collection)

        return arg_config_collection.arg_configs


def _get_arg_kvps(parsed_args, handler):
    # transform parsed args from `argparse` into a dict
    parsed_args = vars(parsed_args)
    kvps = {key.replace(u"-", u"_"): val for (key, val) in parsed_args.items()}
    kvps.pop(u"func", None)
    return _inject_params(kvps, handler)


def _inject_params(kvps, handler):
    """Automatically populates parameters named "sdk" or "profile" with instances of the sdk and 
    profile, respectively.

    Args:
        kvps (dict): A dictionary of the parsed command line arguments.
        handler (callable): The function or command responsible for processing the command line 
            arguments.

    Returns:
        dict: The dictionary of parsed command line arguments with possibly additional populated 
            fields.
    """
    if _handler_has_arg(SDK_ARG_NAME, handler):
        profile_name = kvps.pop(PROFILE_ARG_NAME, None)
        debug = kvps.pop(u"debug", None)

        profile = cliprofile.get_profile(profile_name)
        kvps[SDK_ARG_NAME] = create_sdk(profile, debug)

        if _handler_has_arg(PROFILE_ARG_NAME, handler):
            kvps[PROFILE_ARG_NAME] = profile
    return kvps


def _handler_has_arg(arg_name, handler):
    argspec = inspect.getargspec(handler)
    return arg_name in argspec.args


def _kvps_to_obj(kvps):
    new_kvps = {key: kvps[key] for key in kvps if key in [SDK_ARG_NAME, PROFILE_ARG_NAME]}
    new_kvps[u"args"] = DictObject(kvps)
    return new_kvps


class SubcommandLoader(object):
    """Responsible for creating subcommands for it's root command. It is also useful for getting 
    command information ahead of time, as in the example of tab completion."""

    def __init__(self, root_command_name):
        self.root = root_command_name

    @property
    def names(self):
        """The names of all the subcommands in this subcommabd loader's root command."""
        sub_cmds = self.load_commands()
        return [cmd.name for cmd in sub_cmds]

    @property
    def subtrees(self):
        """All subcommands for this subcommand loader's root command mapped to their given 
        subcommand loaders."""
        cmds = self.load_commands()
        results = {}
        for cmd in cmds:
            subcommand_loader = cmd.subcommand_loader
            if subcommand_loader:
                results[cmd.name] = subcommand_loader
        return results

    def load_commands(self):
        return []
