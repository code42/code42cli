class DetectionLists(object):
    DEPARTING_EMPLOYEE = u"departing-employee"
    HIGH_RISK = u"high-risk"


class BulkCommandType(object):
    ADD = u"add"

    def __iter__(self):
        return iter([self.ADD])
