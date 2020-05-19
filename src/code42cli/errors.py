ERRORED = False


class BadFileError(Exception):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        super(BadFileError, self).__init__()


class EmptyFileError(BadFileError):
    def __init__(self, file_path):
        super(EmptyFileError, self).__init__(file_path, u"Given empty file {}.".format(file_path))
