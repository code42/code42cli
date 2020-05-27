from code42cli import MAIN_COMMAND
from code42cli.main import MainSubcommandLoader


def _get_matches(current, options):
    matches = []
    current = current.strip()
    for opt in options:
        if opt.startswith(current) and opt != current:
            matches.append(opt)
    return matches


class Completer(object):
    def __init__(self, main_cmd_loader=None):
        self._main_cmd_loader = main_cmd_loader or MainSubcommandLoader(u"")
    
    def complete(self, cmdline, point=None):
        try:
            if point is None:
                point = len(cmdline)
            args = cmdline[0:point].split()
            if len(args) < 2:
                if args[0] == MAIN_COMMAND:
                    return self._main_cmd_loader.names
                return []  # `code42` already completes w/o
    
            cmd_loader = self._main_cmd_loader
            current = args[-1]
            if len(args) > 2:
                for arg in args[1:-1]:
                    cmd_loader = cmd_loader.subtrees[arg]
    
            if not cmd_loader:
                return []
            
            options = cmd_loader.names
            if current in options:
                cmd_loader = cmd_loader.subtrees[current]
                return cmd_loader.names
            
            return _get_matches(current, options) if options else []
        except:
            return []


def complete(cmdline, point):
    choices = Completer().complete(cmdline, point)
    print(u" \n".join(choices))
