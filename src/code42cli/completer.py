from code42cli.main import MainCmdNames
from code42cli.cmds.profile import ProfileCmdNames


_cmd_table = {"code42": MainCmdNames(), u"profile": ProfileCmdNames()}


class Completer(object):
    def complete(self, cmdline, point=None):
        args = cmdline[0:point].split()
        if len(args) < 2:
            return []  # `code42` already completes w/o

        current = args[-1]
        last = args[-2]
        options = _cmd_table.get(last)
        if options:
            return self._get_matches(current, options)

        return []

    def _complete_main_cmd(self, current):
        return self._get_matches(current, MainCmdNames())

    def _complete_profile_cmd(self, current):
        return self._get_matches(current, ProfileCmdNames())

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
