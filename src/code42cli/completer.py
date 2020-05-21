from code42cli.main import MainCommandController


class Completer(object):
    def complete(self, cmdline, point=None):
        if point is None:
            point = len(cmdline)
        args = cmdline[0:point].split()
        if len(args) < 2:
            return []  # `code42` already completes w/o

        controller = MainCommandController(u"")
        if len(args) > 2:
            for arg in args[1:-1]:
                controller = controller.table[arg]

        options = controller.names
        current = args[-1]
        return self._get_matches(current, options) if options else []

    def _get_matches(self, current, options):
        matches = []
        current = current.strip()
        for opt in options:
            if opt.startswith(current) and opt != current:
                matches.append(opt)
        return matches


def complete(cmdline, point):
    choices = Completer().complete(cmdline, point)
    print(u" \n".join(choices))
