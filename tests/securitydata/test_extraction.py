import pytest
from datetime import datetime, timedelta

from code42cli.securitydata.options import ExposureType
from .conftest import ROOT_PATH
from code42cli.securitydata.extraction import extract


@pytest.fixture(autouse=True)
def mock_42(mocker):
    mock = mocker.patch("py42.sdk.SDK.create_using_local_account")
    return mock


@pytest.fixture
def logger(mocker):
    mock = mocker.MagicMock()
    mock.info = mocker.MagicMock()
    return mock


@pytest.fixture(autouse=True)
def error_logger(mocker):
    return mocker.patch("{0}.logger_factory".format(ROOT_PATH))


@pytest.fixture
def cursor_store(mocker):
    mock = mocker.patch("c42eventextractor.extractors.AEDCursorStore.__init__")
    mock.return_value = None
    return mock


@pytest.fixture(autouse=True)
def extractor(mocker):
    mock = mocker.MagicMock()
    mock.search_file_events = mocker.patch("c42eventextractor.extractors.AEDEventExtractor.search_file_events")
    mock.extract = mocker.patch("c42eventextractor.extractors.AEDEventExtractor.extract")
    return mock


@pytest.fixture(autouse=True)
def profile(mocker):
    mocker.patch("code42cli.securitydata.extraction.get_profile")


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


def test_extract_when_is_advanced_query_uses_only_the_search_file_events_method(
    logger, namespace, extractor
):
    namespace.advanced_query = "some complex json"
    extract(logger, namespace)
    extractor.search_file_events.assert_called_once_with("some complex json")
    assert extractor.extract.call_count == 0


def test_extract_when_is_advanced_query_and_has_begin_date_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.begin_date = "begin date"
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_end_date_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.end_date = "end date"
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_exposure_types_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.exposure_types = [ExposureType.SHARED_TO_DOMAIN]
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.is_incremental = True
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_set_to_false_does_not_exit(
    logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.is_incremental = False
    extract(logger, namespace)


def test_extract_when_is_not_advanced_query_uses_only_extract_method(logger, extractor, namespace):
    extract(logger, namespace)
    assert extractor.extract.call_count == 1
    assert extractor.search_file_events.call_count == 0


def test_extract_passed_through_given_exposure_types(logger, error_logger, namespace, extractor):
    namespace.exposure_types = [
        ExposureType.IS_PUBLIC,
        ExposureType.CLOUD_STORAGE,
        ExposureType.APPLICATION_READ,
    ]
    extract(logger, namespace)
    assert extractor.extract.call_args[1]["exposure_types"] == [
        ExposureType.IS_PUBLIC,
        ExposureType.CLOUD_STORAGE,
        ExposureType.APPLICATION_READ,
    ]


def test_extract_when_given_begin_date_uses_expected_begin_timestamp(
    logger, error_logger, namespace, extractor
):
    test_begin_date_str = get_test_date_str(days_ago=89)
    namespace.begin_date = test_begin_date_str
    extract(logger, namespace)
    expected_begin_timestamp = get_timestamp_from_date_str(test_begin_date_str)
    actual_begin_timestamp = extractor.extract.call_args[1]["initial_min_timestamp"]
    assert actual_begin_timestamp == expected_begin_timestamp


def test_extract_when_given_begin_date_as_seconds_ago_uses_expected_begin_timestamp(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = "600"
    extract(logger, namespace)
    expected_timestamp = get_timestamp_from_seconds_ago(600)
    actual_timestamp = extractor.extract.call_args[1]["initial_min_timestamp"]
    assert pytest.approx(expected_timestamp, actual_timestamp)


def test_extract_when_given_end_date_uses_expected_begin_timestamp(
    logger, error_logger, namespace, extractor
):
    test_end_date_str = get_test_date_str(days_ago=10)
    namespace.end_date = test_end_date_str
    extract(logger, namespace)
    expected_end_timestamp = get_timestamp_from_date_str(test_end_date_str)
    actual_end_timestamp = extractor.extract.call_args[1]["max_timestamp"]
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_end_date_as_seconds_ago_uses_expected_begin_timestamp(
    logger, error_logger, namespace, extractor
):
    namespace.end_date = "600"
    extract(logger, namespace)
    expected_timestamp = get_timestamp_from_seconds_ago(600)
    actual_timestamp = extractor.extract.call_args[1]["max_timestamp"]
    assert pytest.approx(expected_timestamp, actual_timestamp)


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    logger, error_logger, namespace, extractor
):
    test_begin_date_str = get_test_date_str(days_ago=89)
    namespace.begin_date = test_begin_date_str
    namespace.end_date = "600"
    extract(logger, namespace)

    expected_begin_timestamp = get_timestamp_from_date_str(test_begin_date_str)
    expected_end_timestamp = get_timestamp_from_seconds_ago(600)
    actual_begin_timestamp = extractor.extract.call_args[1]["initial_min_timestamp"]
    actual_end_timestamp = extractor.extract.call_args[1]["max_timestamp"]

    assert actual_begin_timestamp == expected_begin_timestamp
    assert pytest.approx(expected_end_timestamp, actual_end_timestamp)


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = get_test_date_str(days_ago=91)
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = get_test_date_str(days_ago=5)
    namespace.end_date = get_test_date_str(days_ago=6)
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_given_invalid_exposure_type_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.exposure_types = [
        ExposureType.APPLICATION_READ,
        "SomethingElseThatIsNotSupported",
        ExposureType.IS_PUBLIC,
    ]
    with pytest.raises(SystemExit):
        extract(logger, namespace)
