import pytest
from py42.sdk import SDKClient
from py42.sdk.queries.fileevents.filters import *

import code42cli.cmds.securitydata.extraction as extraction_module
from code42cli.cmds.securitydata.enums import ExposureType as ExposureTypeOptions
from .conftest import (
    SECURITYDATA_NAMESPACE,
    begin_date_str,
    get_filter_value_from_json,
    get_test_date_str,
)


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


@pytest.fixture(autouse=True)
def error_logger(mocker):
    return mocker.patch("{0}.extraction.get_error_logger".format(SECURITYDATA_NAMESPACE))


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
    namespace.c42username = ["Someone"]
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


def test_extract_when_is_advanced_query_and_has_filename_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.filename = ["test.out"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_filepath_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.filepath = ["path/to/file"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_process_owner_exits(
    sdk, profile, logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.processOwner = ["someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(sdk, profile, logger, namespace)


def test_extract_when_is_advanced_query_and_has_tab_url_exits(sdk, profile, logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.tabURL = ["https://www.example.com"]
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
    mocker, sdk, profile, logger, namespace, extractor
):
    namespace.begin = "2019-01-01"
    namespace.incremental = True
    mock_checkpoint = mocker.patch(
        "code42cli.cmds.shared.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp"
    )
    mock_checkpoint.return_value = 22624624
    extraction_module.extract(sdk, profile, logger, namespace)
    assert not filter_term_is_in_call_args(extractor, EventTimestamp._term)


def test_when_given_begin_date_and_not_interactive_mode_and_cursor_exists_uses_begin_date(
    mocker, sdk, profile, logger, namespace, extractor
):
    namespace.begin = get_test_date_str(days_ago=1)
    namespace.incremental = False
    mock_checkpoint = mocker.patch(
        "code42cli.cmds.shared.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp"
    )
    mock_checkpoint.return_value = 22624624
    extraction_module.extract(sdk, profile, logger, namespace)

    actual_ts = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected_ts = "{0}T00:00:00.000Z".format(namespace.begin)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(extractor, EventTimestamp._term)


def test_when_not_given_begin_date_and_is_incremental_but_no_stored_checkpoint_exists_causes_exit(
    mocker, sdk, profile, logger, namespace, extractor
):
    namespace.begin = None
    namespace.is_incremental = True
    mock_checkpoint = mocker.patch(
        "code42cli.cmds.shared.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp"
    )
    mock_checkpoint.return_value = None
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
    namespace_with_begin.c42username = ["test.testerson@example.com"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        DeviceUsername.is_in(namespace_with_begin.c42username)
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


def test_extract_when_given_filename_uses_filename_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.filename = ["file.txt", "txt.file"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FileName.is_in(namespace_with_begin.filename)
    )


def test_extract_when_given_filepath_uses_filepath_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.filepath = ["/path/to/file.txt", "path2"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(namespace_with_begin.filepath)
    )


def test_extract_when_given_process_owner_uses_process_owner_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.processOwner = ["test.testerson", "another"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        ProcessOwner.is_in(namespace_with_begin.processOwner)
    )


def test_extract_when_given_tab_url_uses_process_tab_url_filter(
    sdk, profile, logger, namespace_with_begin, extractor
):
    namespace_with_begin.tabURL = ["https://www.example.com"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(TabURL.is_in(namespace_with_begin.tabURL))


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
    namespace_with_begin.filepath = ["/path/to/file.txt"]
    namespace_with_begin.processOwner = ["test.testerson", "flag.flagerson"]
    namespace_with_begin.tabURL = ["https://www.example.com"]
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(namespace_with_begin.filepath)
    )
    assert str(extractor.extract.call_args[0][2]) == str(
        ProcessOwner.is_in(namespace_with_begin.processOwner)
    )
    assert str(extractor.extract.call_args[0][3]) == str(TabURL.is_in(namespace_with_begin.tabURL))


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


def test_extract_when_global_variable_is_true_and_is_interactive_prints_error(
    mocker, sdk, profile, logger, namespace_with_begin, extractor
):
    mock_error_printer = mocker.patch("code42cli.cmds.securitydata.extraction.print_error")
    mock_is_interactive_function = mocker.patch(
        "code42cli.cmds.securitydata.extraction.is_interactive"
    )
    mock_is_interactive_function.return_value = True
    extraction_module._EXCEPTIONS_OCCURRED = True
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert mock_error_printer.call_count


def test_extract_when_global_variable_is_true_and_not_is_interactive_does_not_print_error(
    mocker, sdk, profile, logger, namespace_with_begin, extractor
):
    mock_error_printer = mocker.patch("code42cli.cmds.securitydata.extraction.print_error")
    mock_is_interactive_function = mocker.patch(
        "code42cli.cmds.securitydata.extraction.is_interactive"
    )
    mock_is_interactive_function.return_value = False
    extraction_module._EXCEPTIONS_OCCURRED = True
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert not mock_error_printer.call_count


def test_extract_when_global_variable_is_false_and_is_interactive_does_not_print_error(
    mocker, sdk, profile, logger, namespace_with_begin, extractor
):
    mock_error_printer = mocker.patch("code42cli.cmds.securitydata.extraction.print_error")
    mock_is_interactive_function = mocker.patch(
        "code42cli.cmds.securitydata.extraction.is_interactive"
    )
    mock_is_interactive_function.return_value = True
    extraction_module._EXCEPTIONS_OCCURRED = False
    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert not mock_error_printer.call_count


def test_when_sdk_raises_exception_global_variable_gets_set(
    mocker, sdk, profile, logger, namespace_with_begin, mock_42
):
    extraction_module._EXCEPTIONS_OCCURRED = False
    mock_sdk = mocker.MagicMock()

    # For ease
    mock = mocker.patch("code42cli.cmds.securitydata.extraction.is_interactive")
    mock.return_value = False

    def sdk_side_effect(self, *args):
        raise Exception()

    mock_sdk.security.search_file_events.side_effect = sdk_side_effect
    mock_42.return_value = mock_sdk

    mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor._verify_compatibility_of_filter_groups"
    )

    extraction_module.extract(sdk, profile, logger, namespace_with_begin)
    assert extraction_module._EXCEPTIONS_OCCURRED
