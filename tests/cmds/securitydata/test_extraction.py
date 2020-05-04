import pytest
import logging

from py42.sdk import SDKClient
from py42.sdk.queries.fileevents.filters import *

import code42cli.cmds.securitydata.extraction as extraction_module
import code42cli.errors as errors
from code42cli import PRODUCT_NAME
from code42cli.cmds.securitydata.enums import ExposureType as ExposureTypeOptions
from .conftest import get_filter_value_from_json
from ...conftest import get_test_date_str, begin_date_str, ErrorTrackerTestHelper


@pytest.fixture
def sdk(mocker):
    return mocker.MagicMock(spec=SDKClient)


@pytest.fixture()
def mock_42(mocker):
    return mocker.patch("py42.sdk.from_local_account")


@pytest.fixture
def logger(mocker):
    mock = mocker.MagicMock()
    mock.info = mocker.MagicMock()
    return mock


@pytest.fixture
def extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_advanced = mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor.extract_advanced"
    )
    mock.extract = mocker.patch("c42eventextractor.extractors.FileEventExtractor.extract")
    return mock


@pytest.fixture
def namespace_with_begin(namespace):
    namespace.begin = begin_date_str
    return namespace


@pytest.fixture
def checkpoint(mocker):
    return mocker.patch(
        "{}.cmds.shared.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp".format(
            PRODUCT_NAME
        )
    )


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


def test_extract_when_is_advanced_query_uses_only_the_extract_advanced(
    sdk, profile, logger, namespace, extractor
):
    namespace.advanced_query = "some complex json"
    extraction_module.extract(sdk, profile, logger, namespace)
    extractor.extract_advanced.assert_called_once_with("some complex json")
    assert extractor.extract.call_count == 0


def test_extract_when_is_advanced_query_and_has_begin_date_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.begin = "begin date"
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_end_date_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.end = "end date"
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_exposure_types_exits(
    sdk, profile, logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.type = [ExposureTypeOptions.SHARED_TO_DOMAIN]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_username_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.c42_username = ["Someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_actor_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.actor = ["Someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_md5_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.md5 = ["098f6bcd4621d373cade4e832627b4f6"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_sha256_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.sha256 = ["9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_source_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.source = ["Gmail"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_file_name_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.file_name = ["test.out"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_file_path_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.file_path = ["path/to/file"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_process_owner_exits(
    sdk, profile, logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.process_owner = ["someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_tab_url_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.tab_url = ["https://www.example.com"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_exits(
    sdk, profile, logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.incremental = True
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_include_non_exposure_exits(
    sdk, profile, logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.include_non_exposure = True
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_include_non_exposure_is_false_does_not_exit(
    sdk, profile, logger, namespace
):
    namespace.include_non_exposure = False
    namespace.advanced_query = "some complex json"
    extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_set_to_false_does_not_exit(
    sdk, profile, logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.is_incremental = False
    extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_not_advanced_query_uses_only_extract_method(
    sdk, profile, logger, extractor, namespace_with_begin
):
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert extractor.extract.call_count == 1
    assert extractor.extract_raw.call_count == 0


def test_extract_when_not_given_begin_or_advanced_causes_exit(
    sdk, profile, logger, extractor, namespace
):
    namespace.begin = None
    namespace.advanced_query = None
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_given_begin_date_uses_expected_query(
    sdk, profile, logger, namespace, extractor
):
    namespace.begin = get_test_date_str(days_ago=89)
    extraction_module.extract(sdk, profile, logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected = "{0}T00:00:00.000Z".format(namespace.begin)
    assert actual == expected


def test_extract_when_given_begin_date_and_time_uses_expected_query(
    sdk, profile, logger, namespace, extractor
):
    date = get_test_date_str(days_ago=89)
    time = "15:33:02"
    namespace.begin = get_test_date_str(days_ago=89) + " " + time
    extraction_module.extract(sdk, profile, logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected = "{0}T{1}.000Z".format(date, time)
    assert actual == expected


def test_extract_when_given_end_date_uses_expected_query(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.end = get_test_date_str(days_ago=10)
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=1)
    expected = "{0}T23:59:59.999Z".format(namespace_with_begin.end)
    assert actual == expected


def test_extract_when_given_end_date_and_time_uses_expected_query(
    sdk, profile, logger, namespace_with_begin, extractor
):
    date = get_test_date_str(days_ago=10)
    time = "12:00:11"
    namespace_with_begin.end = date + " " + time
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=1)
    expected = "{0}T{1}.000Z".format(date, time)
    assert actual == expected


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    sdk, profile, logger, namespace, extractor
):
    end_date = get_test_date_str(days_ago=55)
    end_time = "13:44:44"
    namespace.begin = get_test_date_str(days_ago=89)
    namespace.end = end_date + " " + end_time
    extraction_module.extract(sdk, profile, logger, namespace)

    actual_begin_timestamp = get_filter_value_from_json(
        extractor.extract.call_args[0][0], filter_index=0
    )
    actual_end_timestamp = get_filter_value_from_json(
        extractor.extract.call_args[0][0], filter_index=1
    )
    expected_begin_timestamp = "{0}T00:00:00.000Z".format(namespace.begin)
    expected_end_timestamp = "{0}T{1}.000Z".format(end_date, end_time)

    assert actual_begin_timestamp == expected_begin_timestamp
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_in_ad_hoc_mode_causes_exit(
    sdk, profile, logger, namespace, extractor
):
    namespace.incremental = False
    date = get_test_date_str(days_ago=91) + " 12:51:00"
    namespace.begin = date
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(
    sdk, profile, logger, namespace, extractor
):
    namespace.begin = get_test_date_str(days_ago=5)
    namespace.end = get_test_date_str(days_ago=6)
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_when_given_begin_date_past_90_days_and_is_incremental_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    sdk, profile, logger, namespace, extractor, checkpoint
):
    namespace.begin = "2019-01-01"
    namespace.incremental = True
    checkpoint.return_value = 22624624
    extraction_module.extract(sdk, profile, logger, namespace)
    assert not filter_term_is_in_call_args(extractor, EventTimestamp._term)


def test_when_given_begin_date_and_not_incremental_mode_and_cursor_exists_uses_begin_date(
    sdk, profile, logger, namespace, extractor
):
    namespace.begin = get_test_date_str(days_ago=1)
    namespace.incremental = False
    checkpoint.return_value = 22624624
    extraction_module.extract(sdk, profile, logger, namespace)

    actual_ts = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected_ts = "{0}T00:00:00.000Z".format(namespace.begin)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(extractor, EventTimestamp._term)


def test_when_not_given_begin_date_and_is_incremental_but_no_stored_checkpoint_exists_causes_exit(
    sdk, profile, logger, namespace, extractor
):
    namespace.begin = None
    namespace.is_incremental = True
    checkpoint.return_value = None
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_given_invalid_exposure_type_causes_exit(
    sdk, profile, logger, namespace, extractor
):
    namespace.type = [
        ExposureTypeOptions.APPLICATION_READ,
        "SomethingElseThatIsNotSupported",
        ExposureTypeOptions.IS_PUBLIC,
    ]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_given_username_uses_username_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.c42_username = ["test.testerson@example.com"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        DeviceUsername.is_in(namespace_with_begin.c42_username)
    )


def test_extract_when_given_actor_uses_actor_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.actor = ["test.testerson"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(Actor.is_in(namespace_with_begin.actor))


def test_extract_when_given_md5_uses_md5_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.md5 = ["098f6bcd4621d373cade4e832627b4f6"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(MD5.is_in(namespace_with_begin.md5))


def test_extract_when_given_sha256_uses_sha256_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.sha256 = [
        "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    ]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(SHA256.is_in(namespace_with_begin.sha256))


def test_extract_when_given_source_uses_source_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.source = ["Gmail", "Yahoo"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(Source.is_in(namespace_with_begin.source))


def test_extract_when_given_file_name_uses_file_name_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.file_name = ["file.txt", "txt.file"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FileName.is_in(namespace_with_begin.file_name)
    )


def test_extract_when_given_file_path_uses_file_path_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.file_path = ["/path/to/file.txt", "path2"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(namespace_with_begin.file_path)
    )


def test_extract_when_given_process_owner_uses_process_owner_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.process_owner = ["test.testerson", "another"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        ProcessOwner.is_in(namespace_with_begin.process_owner)
    )


def test_extract_when_given_tab_url_uses_process_tab_url_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.tab_url = ["https://www.example.com"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(TabURL.is_in(namespace_with_begin.tab_url))


def test_extract_when_given_exposure_types_uses_exposure_type_is_in_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.type = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        ExposureType.is_in(namespace_with_begin.type)
    )


def test_extract_when_given_include_non_exposure_does_not_include_exposure_type_exists(
    mocker, sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.include_non_exposure = True
    ExposureType.exists = mocker.MagicMock()
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert not ExposureType.exists.call_count


def test_extract_when_not_given_include_non_exposure_includes_exposure_type_exists(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.include_non_exposure = False
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(ExposureType.exists())


def test_extract_when_given_multiple_search_args_uses_expected_filters(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.file_path = ["/path/to/file.txt"]
    namespace_with_begin.process_owner = ["test.testerson", "flag.flagerson"]
    namespace_with_begin.tab_url = ["https://www.example.com"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(namespace_with_begin.file_path)
    )
    assert str(extractor.extract.call_args[0][2]) == str(
        ProcessOwner.is_in(namespace_with_begin.process_owner)
    )
    assert str(extractor.extract.call_args[0][3]) == str(TabURL.is_in(namespace_with_begin.tab_url))


def test_extract_when_given_include_non_exposure_and_exposure_types_causes_exit(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.type = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    namespace_with_begin.include_non_exposure = True
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace_with_begin)


def test_extract_when_creating_sdk_throws_causes_exit(
    sdk, profile, logger, extractor, namespace, mock_42
):
    def side_effect():
        raise Exception()

    mock_42.side_effect = side_effect
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_errored_logs_error_occurred(
    sdk, profile, logger, namespace_with_begin, extractor, caplog,
):
    with ErrorTrackerTestHelper():
        with caplog.at_level(logging.ERROR):
            extraction_module.extract(sdk, profile, logger, namespace_with_begin)
            assert "ERROR" in caplog.text
            assert "View exceptions that occurred at" in caplog.text


def test_extract_when_not_errored_and_does_not_log_error_occurred(
    sdk, profile, logger, namespace_with_begin, extractor, caplog,
):
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    with caplog.at_level(logging.ERROR):
        assert "View exceptions that occurred at" not in caplog.text


def test_when_handle_event_raises_exception_global_variable_gets_set(
    mocker, sdk, extractor, profile, logger, namespace_with_begin, mock_42
):
    mock_sdk = mocker.MagicMock()

    def sdk_side_effect(self, *args):
        raise Exception()

    mock_sdk.security.search_file_events.side_effect = sdk_side_effect
    mock_42.return_value = mock_sdk

    mocker.patch(
        "c42eventextractor.extractors.BaseExtractor._verify_filter_groups"
    )
    with ErrorTrackerTestHelper():
        extraction_module.extract(sdk, profile, logger, namespace_with_begin)
        assert errors.ERRORED
