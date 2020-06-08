import pytest
from code42cli.cmds.securitydata.savedsearch.savedsearch import (
    show,
    show_detail,
    print_out,
    send_to,
    write_to
)
from code42cli.cmds.search_shared import logger_factory


@pytest.fixture
def file_event_extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_advanced = mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor.extract_advanced"
    )
    mock.extract = mocker.patch("c42eventextractor.extractors.FileEventExtractor.extract")
    return mock


def test_show_calls_get_method(sdk_with_user, profile):
    show(sdk_with_user, profile)
    assert sdk_with_user.securitydata.savedsearches.get.call_count == 1


def test_show_detail_calls_get_by_id_method(sdk_with_user, profile):
    show_detail(sdk_with_user, profile, u"test-id")
    sdk_with_user.securitydata.savedsearches.get_by_id.assert_called_once_with(u"test-id")


def test_print_out_calls_execute_method(sdk_with_user, profile, file_event_extractor):
    print_out(sdk_with_user, profile, u"test-id")
    sdk_with_user.securitydata.savedsearches.get_query.assert_called_once_with("test-id")
    assert file_event_extractor.extract_advanced.call_count == 1


def test_write_to_calls_correct_get_method(sdk_with_user, profile, file_event_extractor):
    write_to(sdk_with_user, profile, u"test-id", u"test-file")
    sdk_with_user.securitydata.savedsearches.get_query.assert_called_once_with(u"test-id")
    assert file_event_extractor.extract_advanced.call_count == 1
