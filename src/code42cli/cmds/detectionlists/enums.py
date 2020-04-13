class BulkCommandType(object):
    ADD = u"add"

    def __iter__(self):
        return iter([self.ADD])
