from code42cli.main import MainCmdNames


class Completer(object):

    def complete(self, cmdline, point=None):
        args = cmdline[0:point].split()
        if len(args) == 2:
            return self._complete_main_cmd(args[-1])
        return []

    def _complete_main_cmd(self, current):
        matches = []
        for c in list(MainCmdNames()):
            if c.strip().startswith(current) and c != current:
                matches.append(c)
        return matches


def complete(cmdline, point):
    choices = Completer().complete(cmdline, point)
    print(" \n".join(choices))
