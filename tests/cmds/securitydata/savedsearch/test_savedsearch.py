import pytest
from code42cli.cmds.securitydata.savedsearch.savedsearch import show, show_detail


def test_show_calls_get_method(sdk_with_user, profile):
    show(sdk_with_user, profile)
    assert sdk_with_user.securitydata.savedsearches.get.call_count == 1


def test_show_detail_calls_get_by_id_method(sdk_with_user, profile):
    show_detail(sdk_with_user, profile, u"test-id")
    sdk_with_user.securitydata.savedsearches.get_by_id.assert_called_once_with(u"test-id")
