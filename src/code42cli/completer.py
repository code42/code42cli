from code42cli import MAIN_COMMAND
from code42cli.command_table import get_command_table


class Completer(object):
    def complete(self, cmdline, point=None):
        args = cmdline[0:point].split()
        if len(args) < 2:
            return []  # `code42` already completes w/o

        current = args[-1]
        last = args[-2] if args[-2] != MAIN_COMMAND else u""
        cmd_table = get_command_table()
        options = cmd_table.get(last)
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
