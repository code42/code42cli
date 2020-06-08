class CLINode(object):
    """Base class for identifying nodes in the command/argument hierarchy."""

    @property
    def names(self):
        """Override"""
        return []


class ChoicesNode(CLINode):
    """A node who `names` refer to choices the user can select for an argument."""

    def __init__(self, options):
        self._choices = options

    def __iter__(self):
        return iter(self._choices)

    def __getitem__(self, item):
        return self._choices[item]

    def get(self, item):
        return self._choices.get(item)

    @property
    def names(self):
        return self._choices


class ArgNode(CLINode):
    """A node whose `names` are a list of flagged arguments the user can select from."""

    def __init__(self, args):
        self.args = args

    @property
    def names(self):
        try:
            arg_names = [
                n
                for names in [self.args[key].settings[u"options_list"] for key in self.args]
                for n in names
                if n.startswith("--")
            ]
            return arg_names
        except:
            return self.args

    def __getitem__(self, item):
        """Access sub loaders to navigate the argument/options tree, connected to a leaf command."""
        if item in self.args:
            return ArgNode(self.args)

        for key in self.args:
            arg = self.args[key]
            if item not in arg.settings[u"options_list"]:
                continue
            choices = arg.settings[u"choices"]
            if choices:
                return ChoicesNode(choices)
        return ArgNode(self.args)

    def __iter__(self):
        return iter(self.names)


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
        cmd = self._get_command_by_name(item)
        if cmd:
            args = cmd.get_arg_configs()
            return ArgNode(args)

    def _get_command_by_name(self, name):
        for cmd in self.commands:
            if cmd.name == name:
                return cmd

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
