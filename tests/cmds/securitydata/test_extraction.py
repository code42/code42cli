import pytest
import logging

from py42.sdk.queries.fileevents.filters import *

import code42cli.cmds.securitydata.extraction as extraction_module
import code42cli.errors as errors
from code42cli import PRODUCT_NAME
from code42cli.cmds.search_shared.enums import ExposureType as ExposureTypeOptions
from tests.cmds.conftest import get_filter_value_from_json
from code42cli.errors import DateArgumentError
from ...conftest import get_test_date_str, begin_date_str, ErrorTrackerTestHelper


@pytest.fixture
def file_event_extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_advanced = mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor.extract_advanced"
    )
    mock.extract = mocker.patch("c42eventextractor.extractors.FileEventExtractor.extract")
    return mock


@pytest.fixture
def file_event_namespace_with_begin(file_event_namespace):
    file_event_namespace.begin = begin_date_str
    return file_event_namespace


@pytest.fixture
def file_event_checkpoint(mocker):
    return mocker.patch(
        "{}.cmds.search_shared.cursor_store.FileEventCursorStore.get".format(PRODUCT_NAME)
    )


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


def test_extract_when_is_advanced_query_uses_only_the_extract_advanced(
    sdk, profile, logger, file_event_namespace, file_event_extractor
):
    file_event_namespace.advanced_query = "some complex json"
    extraction_module.extract(sdk, profile, logger, file_event_namespace)
    file_event_extractor.extract_advanced.assert_called_once_with("some complex json")
    assert file_event_extractor.extract.call_count == 0


def test_extract_when_is_advanced_query_and_has_begin_date_exits(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.begin = "begin date"
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_advanced_query_and_has_end_date_exits(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.end = "end date"
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_advanced_query_and_has_exposure_types_exits(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.type = [ExposureTypeOptions.SHARED_TO_DOMAIN]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


@pytest.mark.parametrize(
    "arg",
    [
        "c42_username",
        "actor",
        "md5",
        "sha256",
        "source",
        "file_name",
        "file_path",
        "process_owner",
        "tab_url",
    ],
)
def test_extract_when_is_advanced_query_and_other_incompatible_multi_narg_argument_passed(
    sdk, profile, logger, file_event_namespace, arg
):
    file_event_namespace.advanced_query = "some complex json"
    setattr(file_event_namespace, arg, ["test_value"])
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_advanced_query_and_has_use_checkpoint_mode_exits(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.use_checkpoint = "foo"
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_advanced_query_and_has_include_non_exposure_exits(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.include_non_exposure = True
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_advanced_query_and_include_non_exposure_is_false_does_not_exit(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.include_non_exposure = False
    file_event_namespace.advanced_query = "some complex json"
    extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_set_to_false_does_not_exit(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.use_checkpoint = None
    extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_is_not_advanced_query_uses_only_extract_method(
    sdk, profile, logger, file_event_extractor, file_event_namespace_with_begin
):
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert file_event_extractor.extract.call_count == 1
    assert file_event_extractor.extract_raw.call_count == 0


def test_extract_when_not_given_begin_or_advanced_causes_exit(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.begin = None
    file_event_namespace.advanced_query = None
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_given_begin_date_uses_expected_query(
    sdk, profile, logger, file_event_namespace, file_event_extractor
):
    file_event_namespace.begin = get_test_date_str(days_ago=89)
    extraction_module.extract(sdk, profile, logger, file_event_namespace)
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=0
    )
    expected = "{0}T00:00:00.000Z".format(file_event_namespace.begin)
    assert actual == expected


def test_extract_when_given_begin_date_and_time_uses_expected_query(
    sdk, profile, logger, file_event_namespace, file_event_extractor
):
    date = get_test_date_str(days_ago=89)
    time = "15:33:02"
    file_event_namespace.begin = get_test_date_str(days_ago=89) + " " + time
    extraction_module.extract(sdk, profile, logger, file_event_namespace)
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=0
    )
    expected = "{0}T{1}.000Z".format(date, time)
    assert actual == expected


def test_extract_when_given_end_date_uses_expected_query(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.end = get_test_date_str(days_ago=10)
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=1
    )
    expected = "{0}T23:59:59.999Z".format(file_event_namespace_with_begin.end)
    assert actual == expected


def test_extract_when_given_end_date_and_time_uses_expected_query(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    date = get_test_date_str(days_ago=10)
    time = "12:00:11"
    file_event_namespace_with_begin.end = date + " " + time
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=1
    )
    expected = "{0}T{1}.000Z".format(date, time)
    assert actual == expected


def test_extract_when_given_end_date_and_time_without_seconds_uses_expected_query(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    date = get_test_date_str(days_ago=10)
    time = "12:00"
    file_event_namespace_with_begin.end = date + " " + time
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=1
    )
    expected = "{0}T{1}:00.000Z".format(date, time)
    assert actual == expected


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    sdk, profile, logger, file_event_namespace, file_event_extractor
):
    end_date = get_test_date_str(days_ago=55)
    end_time = "13:44:44"
    file_event_namespace.begin = get_test_date_str(days_ago=89)
    file_event_namespace.end = end_date + " " + end_time
    extraction_module.extract(sdk, profile, logger, file_event_namespace)

    actual_begin_timestamp = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=0
    )
    actual_end_timestamp = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=1
    )
    expected_begin_timestamp = "{0}T00:00:00.000Z".format(file_event_namespace.begin)
    expected_end_timestamp = "{0}T{1}.000Z".format(end_date, end_time)

    assert actual_begin_timestamp == expected_begin_timestamp
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_in_ad_hoc_mode_causes_exit(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.incremental = False
    date = get_test_date_str(days_ago=91) + " 12:51:00"
    file_event_namespace.begin = date
    with pytest.raises(DateArgumentError):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.begin = get_test_date_str(days_ago=5)
    file_event_namespace.end = get_test_date_str(days_ago=6)
    with pytest.raises(DateArgumentError):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_when_given_begin_date_past_90_days_and_uses_checkpoint_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    sdk, profile, logger, file_event_namespace, file_event_extractor, file_event_checkpoint
):
    file_event_namespace.begin = "2019-01-01"
    file_event_namespace.use_checkpoint = "foo"
    file_event_checkpoint.return_value = 22624624
    extraction_module.extract(sdk, profile, logger, file_event_namespace)
    assert not filter_term_is_in_call_args(file_event_extractor, EventTimestamp._term)


def test_when_given_begin_date_and_not_interactive_mode_and_cursor_exists_uses_begin_date(
    sdk, profile, logger, file_event_namespace, file_event_extractor, file_event_checkpoint
):
    file_event_namespace.begin = get_test_date_str(days_ago=1)
    file_event_namespace.use_checkpoint = None
    file_event_checkpoint.return_value = 22624624
    extraction_module.extract(sdk, profile, logger, file_event_namespace)

    actual_ts = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][0], filter_index=0
    )
    expected_ts = "{0}T00:00:00.000Z".format(file_event_namespace.begin)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(file_event_extractor, EventTimestamp._term)


def test_when_not_given_begin_date_and_uses_checkpoint_but_no_stored_checkpoint_exists_causes_exit(
    sdk, profile, logger, file_event_namespace, file_event_checkpoint
):
    file_event_namespace.begin = None
    file_event_namespace.use_checkpoint = "foo"
    file_event_checkpoint.return_value = None
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_given_invalid_exposure_type_causes_exit(
    sdk, profile, logger, file_event_namespace
):
    file_event_namespace.type = [
        ExposureTypeOptions.APPLICATION_READ,
        "SomethingElseThatIsNotSupported",
        ExposureTypeOptions.IS_PUBLIC,
    ]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_given_username_uses_username_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.c42_username = ["test.testerson@example.com"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        DeviceUsername.is_in(file_event_namespace_with_begin.c42_username)
    )


def test_extract_when_given_actor_uses_actor_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.actor = ["test.testerson"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        Actor.is_in(file_event_namespace_with_begin.actor)
    )


def test_extract_when_given_md5_uses_md5_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.md5 = ["098f6bcd4621d373cade4e832627b4f6"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        MD5.is_in(file_event_namespace_with_begin.md5)
    )


def test_extract_when_given_sha256_uses_sha256_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.sha256 = [
        "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    ]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        SHA256.is_in(file_event_namespace_with_begin.sha256)
    )


def test_extract_when_given_source_uses_source_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.source = ["Gmail", "Yahoo"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        Source.is_in(file_event_namespace_with_begin.source)
    )


def test_extract_when_given_file_name_uses_file_name_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.file_name = ["file.txt", "txt.file"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        FileName.is_in(file_event_namespace_with_begin.file_name)
    )


def test_extract_when_given_file_path_uses_file_path_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.file_path = ["/path/to/file.txt", "path2"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(file_event_namespace_with_begin.file_path)
    )


def test_extract_when_given_process_owner_uses_process_owner_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.process_owner = ["test.testerson", "another"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        ProcessOwner.is_in(file_event_namespace_with_begin.process_owner)
    )


def test_extract_when_given_tab_url_uses_process_tab_url_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.tab_url = ["https://www.example.com"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        TabURL.is_in(file_event_namespace_with_begin.tab_url)
    )


def test_extract_when_given_exposure_types_uses_exposure_type_is_in_filter(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.type = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        ExposureType.is_in(file_event_namespace_with_begin.type)
    )


def test_extract_when_given_include_non_exposure_does_not_include_exposure_type_exists(
    mocker, sdk, profile, logger, file_event_namespace_with_begin
):
    file_event_namespace_with_begin.include_non_exposure = True
    ExposureType.exists = mocker.MagicMock()
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert not ExposureType.exists.call_count


def test_extract_when_not_given_include_non_exposure_includes_exposure_type_exists(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.include_non_exposure = False
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(ExposureType.exists())


def test_extract_when_given_multiple_search_args_uses_expected_filters(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor
):
    file_event_namespace_with_begin.file_path = ["/path/to/file.txt"]
    file_event_namespace_with_begin.process_owner = ["test.testerson", "flag.flagerson"]
    file_event_namespace_with_begin.tab_url = ["https://www.example.com"]
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert str(file_event_extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(file_event_namespace_with_begin.file_path)
    )
    assert str(file_event_extractor.extract.call_args[0][2]) == str(
        ProcessOwner.is_in(file_event_namespace_with_begin.process_owner)
    )
    assert str(file_event_extractor.extract.call_args[0][3]) == str(
        TabURL.is_in(file_event_namespace_with_begin.tab_url)
    )


def test_extract_when_given_include_non_exposure_and_exposure_types_causes_exit(
    sdk, profile, logger, file_event_namespace_with_begin
):
    file_event_namespace_with_begin.type = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    file_event_namespace_with_begin.include_non_exposure = True
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)


def test_extract_when_creating_sdk_throws_causes_exit(
    sdk, profile, logger, file_event_namespace, mock_42
):
    def side_effect():
        raise Exception()

    mock_42.side_effect = side_effect
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, file_event_namespace)


def test_extract_when_not_errored_and_does_not_log_error_occurred(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor, caplog
):
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    with caplog.at_level(logging.ERROR):
        assert "View exceptions that occurred at" not in caplog.text


def test_extract_when_not_errored_and_is_interactive_does_not_print_error(
    sdk, profile, logger, file_event_namespace_with_begin, file_event_extractor, cli_logger, mocker
):
    errors.ERRORED = False
    mocker.patch("code42cli.cmds.securitydata.extraction.logger", cli_logger)
    extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
    assert cli_logger.print_and_log_error.call_count == 0
    assert cli_logger.log_error.call_count == 0
    errors.ERRORED = False


def test_when_sdk_raises_exception_global_variable_gets_set(
    mocker, sdk, profile, logger, file_event_namespace_with_begin, mock_42
):
    errors.ERRORED = False
    mock_sdk = mocker.MagicMock()

    def sdk_side_effect(self, *args):
        raise Exception()

    mock_sdk.security.search_file_events.side_effect = sdk_side_effect
    mock_42.return_value = mock_sdk

    mocker.patch("c42eventextractor.extractors.BaseExtractor._verify_filter_groups")
    with ErrorTrackerTestHelper():
        extraction_module.extract(sdk, profile, logger, file_event_namespace_with_begin)
        assert errors.ERRORED
