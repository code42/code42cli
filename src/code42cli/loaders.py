class OptionsLoader(object):
    """A loader's who `names` refer to choices the user can select."""
    
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


class ArgLoader(object):
    """A loader whose `names` are a list of flagged arguments the user can select from."""
    
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
            return OptionsLoader(arg.settings[u"choices"])
        return ArgLoader(self._args)

    def __iter__(self):
        return iter(self._names)


class SubcommandLoader(object):
    """Responsible for creating subcommands for it's root command. It is also useful for getting 
    command information ahead of time, as in the example of tab completion."""

    def __init__(self, root_command_name):
        self.root = root_command_name
        self._cmds = None

    def __getitem__(self, item):
        try:
            return self._subtrees[item]
        except KeyError:
            return self._get_args(item)

    def _get_args(self, item):
        cmds = self._get_commands()
        cmd = [c for c in cmds if c.name == item][0]
        args = cmd.get_arg_configs()
        names = [
            n for names in [args[key].settings[u"options_list"] for key in args] for n in names
        ]
        return ArgLoader(args)

    @property
    def names(self):
        """The names of all the subcommands in this subcommand loader's root command."""
        cmds = self._get_commands()
        # Handle command groups
        if len(cmds) != 1:
            return [cmd.name for cmd in cmds]

    @property
    def _subtrees(self):
        """All subcommands for this subcommand loader's root command mapped to their given 
        subcommand loaders."""
        cmds = self._get_commands()
        results = {}
        for cmd in cmds:
            subcommand_loader = cmd.subcommand_loader
            if subcommand_loader:
                results[cmd.name] = subcommand_loader
        return results

    def load_commands(self):
        """Override"""
        return []

    def _get_commands(self):
        if self._cmds is None:
            self._cmds = self.load_commands()
        return self._cmds
