import pytest
from argparse import Namespace
from datetime import datetime, timedelta

from c42sec._internal.extraction import extract


@pytest.fixture(autouse=True)
def mock_42(mocker):
    mock = mocker.patch("py42.sdk.SDK.create_using_local_account")
    return mock


@pytest.fixture
def mock_logger(mocker):
    mock = mocker.MagicMock()
    mock.info = mocker.MagicMock()
    return mock


@pytest.fixture(autouse=True)
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


def get_test_date_str(days_ago):
    now = datetime.utcnow()
    days_ago_date = now - timedelta(days=days_ago)
    return days_ago_date.strftime("%Y-%m-%d")


def get_timestamp_from_date_str(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return (date - datetime.utcfromtimestamp(0)).total_seconds()


def get_timestamp_from_seconds_ago(seconds_ago):
    date = datetime.utcnow() - timedelta(seconds=seconds_ago)
    return (date - datetime.utcfromtimestamp(0)).total_seconds()


def test_extract_when_is_advanced_query_uses_only_the_extract_raw_method(
    mock_logger, namespace, mock_extractor
):
    namespace.advanced_query = "some complex json"
    extract(mock_logger, namespace)
    mock_extractor.extract_raw.assert_called_once_with("some complex json")
    assert mock_extractor.extract.call_count == 0


def test_extract_when_is_advanced_query_and_has_begin_date_exits(
    mock_logger, namespace, mock_extractor
):
    namespace.advanced_query = "some complex json"
    namespace.begin_date = "begin date"
    with pytest.raises(SystemExit):
        extract(mock_logger, namespace)


def test_extract_when_is_advanced_query_and_has_end_date_exits(
    mock_logger, namespace, mock_extractor
):
    namespace.advanced_query = "some complex json"
    namespace.end_date = "end date"
    with pytest.raises(SystemExit):
        extract(mock_logger, namespace)


def test_extract_when_is_advanced_query_and_has_exposure_types_exits(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    namespace.advanced_query = "some complex json"
    namespace.exposure_types = "exposure"
    with pytest.raises(SystemExit):
        extract(mock_logger, namespace)


def test_extract_when_is_not_advanced_query_uses_only_extract_method(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    extract(mock_logger, namespace)
    assert mock_extractor.extract.call_count == 1
    assert mock_extractor.extract_raw.call_count == 0


def test_extract_passed_through_given_exposure_types(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    namespace.exposure_types = ["exposure"]
    extract(mock_logger, namespace)
    assert mock_extractor.extract.call_args[1]["exposure_types"] == ["exposure"]


def test_extract_when_given_begin_date_uses_expected_begin_timestamp(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    test_begin_date_str = get_test_date_str(days_ago=89)
    namespace.begin_date = test_begin_date_str
    extract(mock_logger, namespace)
    expected_begin_timestamp = get_timestamp_from_date_str(test_begin_date_str)
    actual_begin_timestamp = mock_extractor.extract.call_args[1]["initial_min_timestamp"]
    assert actual_begin_timestamp == expected_begin_timestamp


def test_extract_when_given_begin_date_as_seconds_ago_uses_expected_begin_timestamp(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    namespace.begin_date = "600"
    extract(mock_logger, namespace)
    expected_timestamp = get_timestamp_from_seconds_ago(600)
    actual_timestamp = mock_extractor.extract.call_args[1]["initial_min_timestamp"]
    assert pytest.approx(expected_timestamp, actual_timestamp)


def test_extract_when_given_end_date_uses_expected_begin_timestamp(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    test_end_date_str = get_test_date_str(days_ago=10)
    namespace.end_date = test_end_date_str
    extract(mock_logger, namespace)
    expected_end_timestamp = get_timestamp_from_date_str(test_end_date_str)
    actual_end_timestamp = mock_extractor.extract.call_args[1]["max_timestamp"]
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_end_date_as_seconds_ago_uses_expected_begin_timestamp(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    namespace.end_date = "600"
    extract(mock_logger, namespace)
    expected_timestamp = get_timestamp_from_seconds_ago(600)
    actual_timestamp = mock_extractor.extract.call_args[1]["max_timestamp"]
    assert pytest.approx(expected_timestamp, actual_timestamp)


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    test_begin_date_str = get_test_date_str(days_ago=89)
    namespace.begin_date = test_begin_date_str
    namespace.end_date = "600"
    extract(mock_logger, namespace)

    expected_begin_timestamp = get_timestamp_from_date_str(test_begin_date_str)
    expected_end_timestamp = get_timestamp_from_seconds_ago(600)
    actual_begin_timestamp = mock_extractor.extract.call_args[1]["initial_min_timestamp"]
    actual_end_timestamp = mock_extractor.extract.call_args[1]["max_timestamp"]

    assert actual_begin_timestamp == expected_begin_timestamp
    assert pytest.approx(expected_end_timestamp, actual_end_timestamp)


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_causes_exit(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    namespace.begin_date = get_test_date_str(days_ago=91)
    with pytest.raises(SystemExit):
        extract(mock_logger, namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(
    mock_logger, mock_error_logger, namespace, mock_extractor
):
    namespace.begin_date = get_test_date_str(days_ago=5)
    namespace.end_date = get_test_date_str(days_ago=6)
    with pytest.raises(SystemExit):
        extract(mock_logger, namespace)
