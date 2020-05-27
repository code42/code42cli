import pytest
from code42cli.cmds.detectionlists import DetectionListHandlers
from code42cli.bulk import BulkCommandType
from code42cli.cmds.detectionlists.bulk import (
    BulkHighRiskEmployee,
    BulkDetectionList,
    HighRiskBulkCommandType,
)


def test_bulk_risk_command_type_inheritance():
    risk_tags_command_type = HighRiskBulkCommandType()
    assert risk_tags_command_type.ADD == BulkCommandType.ADD
    assert risk_tags_command_type.ADD_RISK_TAG == u"add-risk-tags"


def test_bulk_detection_list_get_handler_returns_valid_handler():
    handlers = DetectionListHandlers(add=u"x", remove=u"y", load_add=u"z")
    bulk_detection_list = BulkDetectionList()
    handler = bulk_detection_list.get_handler(handlers, BulkCommandType.ADD)
    assert handler == u"x"


def test_bulk_high_risk_employee_get_handler_returns_valid_handler():
    handlers = DetectionListHandlers(add=u"x", remove=u"y", load_add=u"z")
    handlers.add_handler(u"add_risk_tags", u"p")
    handlers.add_handler(u"remove_risk_tags", u"q")
    bulk_hre = BulkHighRiskEmployee()
    handler = bulk_hre.get_handler(handlers, HighRiskBulkCommandType.ADD_RISK_TAG)
    assert handler == u"p"
    handler = bulk_hre.get_handler(handlers, HighRiskBulkCommandType.REMOVE_RISK_TAG)
    assert handler == u"q"
