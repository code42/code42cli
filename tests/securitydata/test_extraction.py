import pytest
from datetime import datetime

from py42.sdk.alert_query import Actor
from py42.sdk.file_event_query.device_query import DeviceUsername
from py42.sdk.file_event_query.event_query import Source
from py42.sdk.file_event_query.exposure_query import ExposureType, ProcessOwner, TabURL
from py42.sdk.file_event_query.file_query import FilePath, FileName, SHA256, MD5

from code42cli.securitydata.options import ExposureType as ExposureTypeOptions
from code42cli.securitydata.extraction import extract
from .conftest import ROOT_PATH
from ..conftest import (
    get_filter_value_from_json,
    parse_date_from_filter_value,
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
    namespace.exposure_types = [ExposureTypeOptions.SHARED_TO_DOMAIN]
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


def test_extract_passed_through_given_exposure_types(logger, namespace, extractor):
    namespace.exposure_types = [
        ExposureTypeOptions.IS_PUBLIC,
        ExposureTypeOptions.CLOUD_STORAGE,
        ExposureTypeOptions.APPLICATION_READ,
    ]
    extract(logger, namespace)
    assert extractor.extract.call_args[0][0] == [
        ExposureTypeOptions.IS_PUBLIC,
        ExposureTypeOptions.CLOUD_STORAGE,
        ExposureTypeOptions.APPLICATION_READ,
    ]


def test_extract_when_not_given_begin_or_end_dates_uses_default_query(logger, namespace, extractor):
    namespace.begin_date = None
    namespace.end_date = None
    extract(logger, namespace)
    actual_begin = parse_date_from_filter_value(extractor.extract.call_args[0][1], filter_index=0)
    actual_end = parse_date_from_filter_value(extractor.extract.call_args[0][1], filter_index=1)
    expected_begin = get_test_date(days_ago=60)
    expected_end = datetime.utcnow()
    assert (expected_begin - actual_begin).total_seconds() < 0.1
    assert (expected_end - actual_end).total_seconds() < 0.1


def test_extract_when_given_begin_date_uses_expected_query(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=89),)
    extract(logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][1], filter_index=0)
    expected = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    assert actual == expected


def test_extract_when_given_begin_date_and_time_uses_expected_query(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=89), "15:33:02")
    extract(logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][1], filter_index=0)
    expected = "{0}T{1}.000Z".format(namespace.begin_date[0], namespace.begin_date[1])
    assert actual == expected


def test_extract_when_given_end_date_uses_expected_query(logger, namespace, extractor):
    namespace.end_date = (get_test_date_str(days_ago=10),)
    extract(logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][1], filter_index=1)
    expected = "{0}T00:00:00.000Z".format(namespace.end_date[0])
    assert actual == expected


def test_extract_when_given_end_date_and_time_uses_expected_query(logger, namespace, extractor):
    namespace.end_date = (get_test_date_str(days_ago=10), "12:00:11")
    extract(logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][1], filter_index=1)
    expected = "{0}T{1}.000Z".format(namespace.end_date[0], namespace.end_date[1])
    assert actual == expected


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=89),)
    namespace.end_date = (get_test_date_str(days_ago=55), "13:44:44")
    extract(logger, namespace)

    actual_begin_timestamp = get_filter_value_from_json(
        extractor.extract.call_args[0][1], filter_index=0
    )
    actual_end_timestamp = get_filter_value_from_json(
        extractor.extract.call_args[0][1], filter_index=1
    )
    expected_begin_timestamp = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    expected_end_timestamp = "{0}T{1}.000Z".format(namespace.end_date[0], namespace.end_date[1])

    assert actual_begin_timestamp == expected_begin_timestamp
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_causes_exit(
    logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=91), "12:51:00")
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=5),)
    namespace.end_date = (get_test_date_str(days_ago=6),)
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_given_invalid_exposure_type_causes_exit(logger, namespace, extractor):
    namespace.exposure_types = [
        ExposureTypeOptions.APPLICATION_READ,
        "SomethingElseThatIsNotSupported",
        ExposureTypeOptions.IS_PUBLIC,
    ]
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_given_begin_date_with_len_3_causes_exit(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=5), "12:00:00", "+600")
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_given_end_date_with_len_3_causes_exit(logger, namespace, extractor):
    namespace.end_date = (get_test_date_str(days_ago=5), "12:00:00", "+600")
    with pytest.raises(SystemExit):
        extract(logger, namespace)


def test_extract_when_given_username_uses_username_filter(logger, namespace, extractor):
    namespace.c42username = "test.testerson@example.com"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(DeviceUsername.eq(namespace.c42username))


def test_extract_when_given_actor_uses_actor_filter(logger, namespace, extractor):
    namespace.actor = "test.testerson"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(Actor.eq(namespace.actor))


def test_extract_when_given_md5_uses_md5_filter(logger, namespace, extractor):
    namespace.md5 = "098f6bcd4621d373cade4e832627b4f6"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(MD5.eq(namespace.md5))


def test_extract_when_given_sha256_uses_sha256_filter(logger, namespace, extractor):
    namespace.sha256 = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(SHA256.eq(namespace.sha256))


def test_extract_when_given_source_uses_source_filter(logger, namespace, extractor):
    namespace.source = "Gmail"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(Source.eq(namespace.source))


def test_extract_when_given_filename_uses_filename_filter(logger, namespace, extractor):
    namespace.filename = "file.txt"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(FileName.eq(namespace.filename))


def test_extract_when_given_filepath_uses_filepath_filter(logger, namespace, extractor):
    namespace.filepath = "/path/to/file.txt"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(FilePath.eq(namespace.filepath))


def test_extract_when_given_process_owner_uses_process_owner_filter(logger, namespace, extractor):
    namespace.process_owner = "test.testerson"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(ProcessOwner.eq(namespace.process_owner))


def test_extract_when_given_tab_url_uses_process_tab_url_filter(logger, namespace, extractor):
    namespace.tab_url = "https://www.example.com"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(TabURL.eq(namespace.tab_url))


def test_extract_when_given_exposure_types_uses_exposure_type_is_in_filter(
    logger, namespace, extractor
):
    namespace.exposure_types = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(
        ExposureType.is_in(namespace.exposure_types)
    )


def test_extract_when_given_include_non_exposure_does_not_include_exposure_type_exists(
    mocker, logger, namespace, extractor
):
    namespace.include_non_exposure_events = True
    ExposureType.exists = mocker.MagicMock()
    extract(logger, namespace)
    assert not ExposureType.exists.call_count


#
# def test_extract_when_not_given_include_non_exposure_includes_exposure_type_exists(
#     logger, namespace, extractor
# ):
#     namespace.include_non_exposure_events = False
#     extract(logger, namespace)
#     actual_value = get_filter_value_from_json(extractor.extract.call_args[0][2], filter_index=0)
#     actual_term = get_filter_term_from_json(extractor.extract.call_args[0][2], filter_index=0)
#
#
#     #assert str(extractor.extract.call_args[0][2]) == str(ExposureType.exists())
#
#     assert actual_term == "exposure"
#     assert actual_value is None  # For exists(), the value is None


def test_extract_when_given_multiple_search_args_uses_expected_filters(
    logger, namespace, extractor
):
    namespace.filepath = "/path/to/file.txt"
    namespace.process_owner = "test.testerson"
    namespace.tab_url = "https://www.example.com"
    extract(logger, namespace)
    assert str(extractor.extract.call_args[0][2]) == str(FilePath.eq("/path/to/file.txt"))
    assert str(extractor.extract.call_args[0][3]) == str(ProcessOwner.eq("test.testerson"))
    assert str(extractor.extract.call_args[0][4]) == str(TabURL.eq("https://www.example.com"))


def test_extract_when_given_include_non_exposure_and_exposure_types_causes_exit(
    logger, namespace, extractor
):
    namespace.exposure_types = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    namespace.include_non_exposure_events = True
    with pytest.raises(SystemExit):
        extract(logger, namespace)
