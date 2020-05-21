from code42cli.main import MainSubcommandLoader


def _get_matches(current, options):
    matches = []
    current = current.strip()
    for opt in options:
        if opt.startswith(current) and opt != current:
            matches.append(opt)
    return matches


class Completer(object):
    def complete(self, cmdline, point=None):
        if point is None:
            point = len(cmdline)
        args = cmdline[0:point].split()
        if len(args) < 2:
            return []  # `code42` already completes w/o

        cmd_loader = MainSubcommandLoader(u"")
        if len(args) > 2:
            for arg in args[1:-1]:
                cmd_loader = cmd_loader.subtrees[arg]

        if not cmd_loader:
            return []

        options = cmd_loader.names
        current = args[-1]
        return _get_matches(current, options) if options else []


def complete(cmdline, point):
    choices = Completer().complete(cmdline, point)
    print(u" \n".join(choices))
