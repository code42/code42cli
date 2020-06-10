from integration import run_command


class cleanup(object):
    def __init__(self, filename):    
        self.filename = filename

    def __enter__(self):
        return open(self.filename, "r")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        run_command("rm -f {}".format(self.filename))
