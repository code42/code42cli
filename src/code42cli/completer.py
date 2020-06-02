from code42cli import MAIN_COMMAND
from code42cli.main import MainSubcommandLoader
from code42cli.tree_nodes import FileNameArgNode
from code42cli.util import get_local_files


def _get_matches(current, options):
    matches = []
    current = current.strip()
    for opt in options:
        if opt.startswith(current) and opt != current:
            matches.append(opt)
    return matches


def _get_next_full_set_of_options(node, current):
    node = node[current]

    # Complete positional filename with list of local files
    if _should_complete_with_local_files(current, node):
        return get_local_files()

    return node.names


def _should_complete_with_local_files(current, node):
    """If `filename` arg exists and are not typing a flag, try completing with local files."""
    if isinstance(node, FileNameArgNode):
        if not current:
            return True
        return current[0] != u"-"


class Completer(object):
    def __init__(self, main_cmd_loader=None):
        self._main_cmd_loader = main_cmd_loader or MainSubcommandLoader()

    def complete(self, cmdline, point=None):
        try:
            point = point or len(cmdline)
            args = cmdline[0:point].split()
            # Complete with main commands if `code42` is typed out.
            # Note that the command `code42` should complete on its own.
            if len(args) < 2:
                return self._main_cmd_loader.names if args[0] == MAIN_COMMAND else []

            current = args[-1]
            search_results, options = self._get_completion_options(args)

            # Complete with local files
            if _should_complete_with_local_files(current, search_results):
                return _get_matches(current, get_local_files())

            # Complete with full set of arg/command options
            if current in options:
                return _get_next_full_set_of_options(search_results, current)

            # Complete with matching arg/commands
            return _get_matches(current, options) if options else []
        except:
            return []

    def _search_trees(self, args):
        # Find cmd_loader at lowest level from given args
        node = self._main_cmd_loader.get_node()
        if len(args) > 2:
            for arg in args[1:-1]:
                next_node = node[arg]
                if next_node:
                    node = next_node
                else:
                    return node
        return node

    def _get_completion_options(self, args):
        search_results = self._search_trees(args)
        return search_results, search_results.names


def complete(cmdline, point):
    choices = Completer().complete(cmdline, point) or []
    print(u" \n".join(choices))
