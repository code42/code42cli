class Completer(object):
    def complete(self, cmdline, point=None):
        if point is None:
            point = len(cmdline)

        # args = cmdline[0:point].split()
        # current_arg = args[-1]
        # cmd_args = [w for w in args if not w.startswith("-")]
        # opts = [w for w in args if w.startswith("-")]
        return ["departing-employee"]

def complete(cmdline, point):
    choices = Completer().complete(cmdline, point)
    print(' \n'.join(choices))
