import pytest
from code42cli import PRODUCT_NAME
from code42cli.cmds.securitydata.savedsearch.savedsearch import (
    show,
    show_detail,
    print_out,
    send_to,
    write_to
)

@pytest.fixture
def mock_logger_factory(mocker):
    return mocker.patch("{}.cmds.securitydata.main.logger_factory".format(PRODUCT_NAME))


@pytest.fixture
def file_event_extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_advanced = mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor.extract_advanced"
    )
    mock.extract = mocker.patch("c42eventextractor.extractors.FileEventExtractor.extract")
    return mock


@pytest.fixture
def mock_extract(mocker):
    return mocker.patch("{}.cmds.securitydata.extraction.extract_saved_search".format(PRODUCT_NAME))



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


def test_send_to_calls_correct_get_method(
    sdk_with_user,
    profile,
    mocker,
    mock_extract,
    mock_logger_factory
):
    query = "file-event-query-dictionary"
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_server.return_value = logger
    sdk_with_user.securitydata.savedsearches.get_query.return_value = query
    send_to(sdk_with_user, profile, u"test-id", u"localhost", u"UDP")
    sdk_with_user.securitydata.savedsearches.get_query.assert_called_once_with(u"test-id")
    # mock_extract.assert_called_with(sdk_with_user, profile, logger, query, True)
