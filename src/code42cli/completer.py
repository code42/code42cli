from code42cli import MAIN_COMMAND
from code42cli.main import MainSubcommandLoader
from code42cli.loaders import ArgLoader
from code42cli.util import get_local_files


def _get_matches(current, options):
    matches = []
    current = current.strip()
    for opt in options:
        if opt.startswith(current) and opt != current:
            matches.append(opt)
    return matches


def _get_next_full_set_of_commands(loader, current):
    loader = loader[current]

    # Complete positional filename with list of local files
    if isinstance(loader, ArgLoader) and loader.contains_filename and current[0] != u"-":
        return get_local_files()

    return loader.names


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

            # Complete with full set of arg/command options
            if current in options:
                return _get_next_full_set_of_commands(loader, current)

            # Complete with matching arg/commands
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
    choices = Completer().complete(cmdline, point) or []
    print(u" \n".join(choices))
