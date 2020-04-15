class DetectionLists(object):
    DEPARTING_EMPLOYEE = u"departing-employee"
    HIGH_RISK_EMPLOYEE = u"high-risk-employee"


class BulkCommandType(object):
    ADD = u"add"

    def __iter__(self):
        return iter([self.ADD])
