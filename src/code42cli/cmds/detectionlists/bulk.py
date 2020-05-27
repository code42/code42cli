from code42cli.bulk import BulkCommandType


class HighRiskBulkCommandType(BulkCommandType):
    ADD_RISK_TAG = u"add-risk-tags"
    REMOVE_RISK_TAG = u"remove-risk-tags"

    def __iter__(self):
        parent_items = list(super(HighRiskBulkCommandType, self).__iter__())
        return iter([parent_items[0], parent_items[1], self.ADD_RISK_TAG, self.REMOVE_RISK_TAG])


class BulkDetectionList(object):
    def __init__(self):
        self.type = BulkCommandType

    def get_handler(self, handlers, cmd):
        handler = None
        if cmd == self.type.ADD:
            handler = handlers.add_employee
        elif cmd == self.type.REMOVE:
            handler = handlers.remove_employee
        return handler


class BulkHighRiskEmployee(BulkDetectionList):
    def __init__(self):
        super(BulkHighRiskEmployee, self).__init__()
        self.type = HighRiskBulkCommandType

    def get_handler(self, handlers, cmd):
        handler = super(BulkHighRiskEmployee, self).get_handler(handlers, cmd)
        if not handler:
            if cmd == self.type.ADD_RISK_TAG:
                handler = handlers.add_risk_tags
            elif cmd == self.type.REMOVE_RISK_TAG:
                handler = handlers.remove_risk_tags

        return handler
