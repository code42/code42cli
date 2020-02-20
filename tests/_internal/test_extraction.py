import pytest
from argparse import Namespace
from datetime import datetime, timedelta

from c42sec._internal.extraction import extract


@pytest.fixture
def mock_42(mocker):
    mock = mocker.patch("py42.sdk.SDK.create_using_local_account")
    return mock


@pytest.fixture
def mock_logger(mocker):
    mock = mocker.MagicMock()
    mock.info = mocker.MagicMock()
    return mock


@pytest.fixture
def mock_error_logger(mocker):
    return mocker.patch("c42sec._internal.logger_factory")


@pytest.fixture
def mock_store(mocker):
    mock = mocker.patch("c42secevents.extractors.AEDCursorStore.__init__")
    mock.return_value = None
    return mock


@pytest.fixture
def mock_extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_raw = mocker.patch("c42secevents.extractors.AEDEventExtractor.extract_raw")
    mock.extract = mocker.patch("c42secevents.extractors.AEDEventExtractor.extract")
    return mock


@pytest.fixture
def mock_namespace_args(mocker):
    mock = mocker.MagicMock(spec=Namespace)
    mock.is_incremental = None
    mock.advanced_query = None
    mock.is_debug_mode = None
    mock.begin_date = None
    mock.end_date = None
    mock.exposure_types = None
    return mock


def test_extract_when_is_advanced_query_uses_only_the_extract_raw_method(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.advanced_query = "some complex json"
    extract(mock_logger, mock_namespace_args)
    mock_extractor.extract_raw.assert_called_once_with("some complex json")
    assert mock_extractor.extract.call_count == 0


def test_extract_when_is_advanced_query_and_has_begin_date_exits(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.advanced_query = "some complex json"
    mock_namespace_args.begin_date = "begin date"
    with pytest.raises(SystemExit):
        extract(mock_logger, mock_namespace_args)


def test_extract_when_is_advanced_query_and_has_end_date_exits(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.advanced_query = "some complex json"
    mock_namespace_args.end_date = "end date"
    with pytest.raises(SystemExit):
        extract(mock_logger, mock_namespace_args)


def test_extract_when_is_advanced_query_and_has_exposure_types_exits(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.advanced_query = "some complex json"
    mock_namespace_args.exposure_types = "exposure"
    with pytest.raises(SystemExit):
        extract(mock_logger, mock_namespace_args)


def test_extract_when_is_not_advanced_query_uses_only_extract_method(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    extract(mock_logger, mock_namespace_args)
    assert mock_extractor.extract.call_count == 1
    assert mock_extractor.extract_raw.call_count == 0


def test_extract_when_given_begin_date_uses_expected_begin_timestamp(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.begin_date = "2020-08-04"
    extract(mock_logger, mock_namespace_args)
    assert mock_extractor.extract.call_args[1]["initial_min_timestamp"] == 1596499200.0


def test_extract_when_given_begin_date_as_seconds_ago_uses_expected_begin_timestamp(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.begin_date = "600"
    extract(mock_logger, mock_namespace_args)
    expected_time = (datetime.utcnow() - timedelta(seconds=600))
    expected_timestamp = (expected_time - datetime.utcfromtimestamp(0)).total_seconds()
    actual_timestamp = mock_extractor.extract.call_args[1]["initial_min_timestamp"]
    assert pytest.approx(expected_timestamp, actual_timestamp)


def test_extract_when_given_end_date_uses_expected_begin_timestamp(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.end_date = "2020-08-04"
    extract(mock_logger, mock_namespace_args)
    assert mock_extractor.extract.call_args[1]["max_timestamp"] == 1596499200.0


def test_extract_when_given_end_date_as_seconds_ago_uses_expected_begin_timestamp(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.end_date = "600"
    extract(mock_logger, mock_namespace_args)
    expected_time = (datetime.utcnow() - timedelta(seconds=600))
    expected_timestamp = (expected_time - datetime.utcfromtimestamp(0)).total_seconds()
    actual_timestamp = mock_extractor.extract.call_args[1]["max_timestamp"]
    assert pytest.approx(expected_timestamp, actual_timestamp)
