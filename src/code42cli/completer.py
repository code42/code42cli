from code42cli import MAIN_COMMAND
from code42cli.main import MainSubcommandLoader


def _get_matches(current, options):
    matches = []
    current = current.strip()
    for opt in options:
        if opt.startswith(current) and opt != current:
            matches.append(opt)
    return matches


def _get_next_full_set_of_commands(cmd_loader, current):
    cmd_loader = cmd_loader[current]
    return cmd_loader.names


class Completer(object):
    def __init__(self, main_cmd_loader=None):
        self._main_cmd_loader = main_cmd_loader or MainSubcommandLoader()

    def complete(self, cmdline, point=None):
        try:
            point = point or len(cmdline)
            args = cmdline[0:point].split()
            if len(args) < 2:
                # `code42` already completes w/o
                return self._main_cmd_loader.names if args[0] == MAIN_COMMAND else []

            current = args[-1]
            loader = self._search_trees(args)
            options = loader.names
            
            if current in options:
                # `current` is already complete
                return _get_next_full_set_of_commands(loader, current)

            return _get_matches(current, options) if options else []
        except:
            return []

    def _search_trees(self, args):
        # Find cmd_loader at lowest level from given args
        cmd_loader = self._main_cmd_loader
        if len(args) > 2:
            for arg in args[1:-1]:
                new_loader = cmd_loader[arg]
                if new_loader:
                    cmd_loader = new_loader
                else:
                    return cmd_loader
        return cmd_loader


def complete(cmdline, point):
    choices = Completer().complete(cmdline, point)
    print(u" \n".join(choices))
