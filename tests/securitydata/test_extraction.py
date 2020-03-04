import pytest
from datetime import datetime

import code42cli.securitydata.extraction as extraction_module
from code42cli.securitydata.options import ExposureType
from code42cli.securitydata.extraction import extract
from .conftest import ROOT_PATH
from ..conftest import (
    get_first_filter_value_from_json,
    get_second_filter_value_from_json,
    parse_date_from_first_filter_value,
    parse_date_from_second_filter_value,
    get_test_date,
    get_test_date_str,
)


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


@pytest.fixture(autouse=True)
def extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_advanced = mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor.extract_advanced"
    )
    mock.extract = mocker.patch("c42eventextractor.extractors.FileEventExtractor.extract")
    return mock


@pytest.fixture(autouse=True)
def profile(mocker):
    mocker.patch("code42cli.securitydata.extraction.get_profile")


def test_extract_when_is_advanced_query_uses_only_the_extract_advanced(
    logger, namespace, extractor
):
    namespace.advanced_query = "some complex json"
    extract(logger, namespace)
    extractor.extract_advanced.assert_called_once_with("some complex json")
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
    assert extractor.extract_raw.call_count == 0


def test_extract_passed_through_given_exposure_types(logger, error_logger, namespace, extractor):
    namespace.exposure_types = [
        ExposureType.IS_PUBLIC,
        ExposureType.CLOUD_STORAGE,
        ExposureType.APPLICATION_READ,
    ]
    extract(logger, namespace)
    assert extractor.extract.call_args[0][0] == [
        ExposureType.IS_PUBLIC,
        ExposureType.CLOUD_STORAGE,
        ExposureType.APPLICATION_READ,
    ]


def test_extract_when_not_given_begin_or_end_dates_uses_default_query(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = None
    namespace.end_date = None
    extract(logger, namespace)
    actual_begin = parse_date_from_first_filter_value(extractor.extract.call_args[0][1])
    actual_end = parse_date_from_second_filter_value(extractor.extract.call_args[0][1])
    expected_begin = get_test_date(days_ago=60)
    expected_end = datetime.utcnow()
    assert (expected_begin - actual_begin).total_seconds() < 0.1
    assert (expected_end - actual_end).total_seconds() < 0.1


def test_extract_when_given_begin_date_uses_expected_query(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=89),)
    extract(logger, namespace)
    actual = get_first_filter_value_from_json(extractor.extract.call_args[0][1])
    expected = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    assert actual == expected


def test_extract_when_given_begin_date_and_time_uses_expected_query(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=89), "15:33:02")
    extract(logger, namespace)
    actual = get_first_filter_value_from_json(extractor.extract.call_args[0][1])
    expected = "{0}T{1}.000Z".format(namespace.begin_date[0], namespace.begin_date[1])
    assert actual == expected


def test_extract_when_given_end_date_uses_expected_query(
    logger, error_logger, namespace, extractor
):
    namespace.end_date = (get_test_date_str(days_ago=10),)
    extract(logger, namespace)
    actual = get_second_filter_value_from_json(extractor.extract.call_args[0][1])
    expected = "{0}T00:00:00.000Z".format(namespace.end_date[0])
    assert actual == expected


def test_extract_when_given_end_date_and_time_uses_expected_query(
    logger, error_logger, namespace, extractor
):
    namespace.end_date = (get_test_date_str(days_ago=10), "12:00:11")
    extract(logger, namespace)
    actual = get_second_filter_value_from_json(extractor.extract.call_args[0][1])
    expected = "{0}T{1}.000Z".format(namespace.end_date[0], namespace.end_date[1])
    assert actual == expected


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=89),)
    namespace.end_date = (get_test_date_str(days_ago=55), "13:44:44")
    extract(logger, namespace)

    actual_begin_timestamp = get_first_filter_value_from_json(extractor.extract.call_args[0][1])
    actual_end_timestamp = get_second_filter_value_from_json(extractor.extract.call_args[0][1])
    expected_begin_timestamp = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    expected_end_timestamp = "{0}T{1}.000Z".format(namespace.end_date[0], namespace.end_date[1])

    assert actual_begin_timestamp == expected_begin_timestamp
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=91), "12:51:00")
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=5),)
    namespace.end_date = (get_test_date_str(days_ago=6),)
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


def test_extract_when_given_begin_date_with_len_3_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=5), "12:00:00", "+600")
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_given_end_date_with_len_3_causes_exit(
    logger, error_logger, namespace, extractor
):
    namespace.end_date = (get_test_date_str(days_ago=5), "12:00:00", "+600")
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_global_variable_set_print_error(
    mocker, logger, error_logger, namespace, extractor
):
    mock_error_printer = mocker.patch("code42cli.securitydata.extraction.print_error")
    extraction_module._EXCEPTIONS_OCCURRED = True
    extract(logger, namespace)
    assert mock_error_printer.call_count

