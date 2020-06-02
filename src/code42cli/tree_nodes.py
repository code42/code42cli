class CLINode(object):
    """Base class for identifying nodes in the command/argument hierarchy."""

    @property
    def names(self):
        """Override"""
        return []


class ChoicesNode(CLINode):
    """A node who `names` refer to choices the user can select for an argument."""

    def __init__(self, options):
        self._options = options

    def __iter__(self):
        return iter(self._options)

    def __getitem__(self, item):
        return self._options[item]

    def get(self, item):
        return self._options.get(item)

    @property
    def names(self):
        return self._options


class ArgNode(CLINode):
    """A node whose `names` are a list of flagged arguments the user can select from."""

    def __init__(self, args):
        # Only cares about args that the user has to type, not positionals
        self._args = args
        try:
            arg_names = [
                n for names in [args[key].settings[u"options_list"] for key in args] for n in names
            ]
            self.contains_filename = u"filename" in arg_names
            self._names = [n for n in arg_names if n[0] == u"-"]
        except TypeError:
            self._names = args

    @property
    def names(self):
        return self._names

    def __getitem__(self, item):
        """Access sub loaders to navigate the argument/options tree, connected to a leaf command."""
        if item in self._names:
            arg = [
                self._args[key]
                for key in self._args
                if item in self._args[key].settings[u"options_list"]
            ][0]
            return ChoicesNode(arg.settings[u"choices"])
        return ArgNode(self._args)

    def __iter__(self):
        return iter(self._names)


class SubcommandNode(CLINode):
    """Gets command information ahead of command-execution."""

    def __init__(self, root_command_name, commands):
        self.root = root_command_name
        self.commands = commands

    def __getitem__(self, item):
        try:
            return self._subtrees[item]
        except KeyError:
            return self._get_args(item)

    def _get_args(self, item):
        cmd = [c for c in self.commands if c.name == item][0]
        args = cmd.get_arg_configs()
        return ArgNode(args)

    @property
    def names(self):
        """The names of all the subcommands in this subcommand loader's root command."""
        return [cmd.name for cmd in self.commands]

    @property
    def _subtrees(self):
        """Maps subcommand names to their respective subcommand nodes."""
        results = {}
        for cmd in self.commands:
            if cmd.subcommand_loader:
                commands = cmd.subcommand_loader.load_commands()
                results[cmd.name] = SubcommandNode(cmd.name, commands)
        return results
