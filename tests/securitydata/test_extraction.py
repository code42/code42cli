import pytest
from py42.sdk.alert_query import Actor
from py42.sdk.file_event_query.device_query import DeviceUsername
from py42.sdk.file_event_query.event_query import Source, EventTimestamp
from py42.sdk.file_event_query.exposure_query import ExposureType, ProcessOwner, TabURL
from py42.sdk.file_event_query.file_query import FilePath, FileName, SHA256, MD5

import code42cli.securitydata.extraction as extraction_module
from code42cli.securitydata.options import ExposureType as ExposureTypeOptions
from .conftest import SECURITYDATA_NAMESPACE, begin_date_tuple
from ..conftest import get_filter_value_from_json, get_test_date_str


@pytest.fixture(autouse=True)
def mock_42(mocker):
    return mocker.patch("py42.sdk.SDK.create_using_local_account")


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


@pytest.fixture(autouse=True)
def profile(mocker):
    mocker.patch("code42cli.securitydata.extraction.get_profile")


@pytest.fixture
def namespace_with_begin(namespace):
    namespace.begin_date = begin_date_tuple
    return namespace


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


def test_extract_when_is_advanced_query_uses_only_the_extract_advanced(
    logger, namespace, extractor
):
    namespace.advanced_query = "some complex json"
    extraction_module.extract(logger, namespace)
    extractor.extract_advanced.assert_called_once_with("some complex json")
    assert extractor.extract.call_count == 0


def test_extract_when_is_advanced_query_and_has_begin_date_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.begin_date = "begin date"
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_end_date_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.end_date = "end date"
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_exposure_types_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.exposure_types = [ExposureTypeOptions.SHARED_TO_DOMAIN]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_username_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.c42usernames = ["Someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_actor_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.actors = ["Someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_md5_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.md5_hashes = ["098f6bcd4621d373cade4e832627b4f6"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_sha256_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.sha256_hashes = ["9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_source_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.sources = ["Gmail"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_filename_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.filenames = ["test.out"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_filepath_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.filepaths = ["path/to/file"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_process_owner_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.process_owners = ["someone"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_tab_url_exists(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.tab_urls = ["https://www.example.com"]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.is_incremental = True
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_include_non_exposure_exits(logger, namespace):
    namespace.advanced_query = "some complex json"
    namespace.include_non_exposure_events = True
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_include_non_exposure_is_false_does_not_exit(
    logger, namespace
):
    namespace.include_non_exposure_events = False
    namespace.advanced_query = "some complex json"
    extraction_module.extract(logger, namespace)


def test_extract_when_is_advanced_query_and_has_incremental_mode_set_to_false_does_not_exit(
    logger, namespace
):
    namespace.advanced_query = "some complex json"
    namespace.is_incremental = False
    extraction_module.extract(logger, namespace)


def test_extract_when_is_not_advanced_query_uses_only_extract_method(
    logger, extractor, namespace_with_begin
):
    extraction_module.extract(logger, namespace_with_begin)
    assert extractor.extract.call_count == 1
    assert extractor.extract_raw.call_count == 0


def test_extract_when_not_given_begin_or_advanced_causes_exit(logger, extractor, namespace):
    namespace.begin_date = None
    namespace.advanced_query = None
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_given_begin_date_uses_expected_query(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=89),)
    extraction_module.extract(logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    assert actual == expected


def test_extract_when_given_begin_date_and_time_uses_expected_query(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=89), "15:33:02")
    extraction_module.extract(logger, namespace)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected = "{0}T{1}.000Z".format(namespace.begin_date[0], namespace.begin_date[1])
    assert actual == expected


def test_extract_when_given_end_date_uses_expected_query(logger, namespace_with_begin, extractor):
    namespace_with_begin.end_date = (get_test_date_str(days_ago=10),)
    extraction_module.extract(logger, namespace_with_begin)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=1)
    expected = "{0}T23:59:59.000Z".format(namespace_with_begin.end_date[0])
    assert actual == expected


def test_extract_when_given_end_date_and_time_uses_expected_query(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.end_date = (get_test_date_str(days_ago=10), "12:00:11")
    extraction_module.extract(logger, namespace_with_begin)
    actual = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=1)
    expected = "{0}T{1}.000Z".format(
        namespace_with_begin.end_date[0], namespace_with_begin.end_date[1]
    )
    assert actual == expected


def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
    logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=89),)
    namespace.end_date = (get_test_date_str(days_ago=55), "13:44:44")
    extraction_module.extract(logger, namespace)

    actual_begin_timestamp = get_filter_value_from_json(
        extractor.extract.call_args[0][0], filter_index=0
    )
    actual_end_timestamp = get_filter_value_from_json(
        extractor.extract.call_args[0][0], filter_index=1
    )
    expected_begin_timestamp = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    expected_end_timestamp = "{0}T{1}.000Z".format(namespace.end_date[0], namespace.end_date[1])

    assert actual_begin_timestamp == expected_begin_timestamp
    assert actual_end_timestamp == expected_end_timestamp


def test_extract_when_given_min_timestamp_more_than_ninety_days_back_in_ad_hoc_mode_causes_exit(
    logger, namespace, extractor
):
    namespace.is_incremental = False
    namespace.begin_date = (get_test_date_str(days_ago=91), "12:51:00")
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_end_date_is_before_begin_date_causes_exit(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=5),)
    namespace.end_date = (get_test_date_str(days_ago=6),)
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_when_given_begin_date_past_90_days_and_is_incremental_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    mocker, logger, namespace, extractor
):
    namespace.begin_date = "2019-01-01"
    namespace.is_incremental = True
    mock_checkpoint = mocker.patch(
        "code42cli.securitydata.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp"
    )
    mock_checkpoint.return_value = 22624624
    extraction_module.extract(logger, namespace)
    assert not filter_term_is_in_call_args(extractor, EventTimestamp._term)


def test_when_given_begin_date_and_not_interactive_mode_and_cursor_exists_uses_begin_date(
    mocker, logger, namespace, extractor
):
    namespace.begin_date = (get_test_date_str(days_ago=1),)
    namespace.is_incremental = False
    mock_checkpoint = mocker.patch(
        "code42cli.securitydata.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp"
    )
    mock_checkpoint.return_value = 22624624
    extraction_module.extract(logger, namespace)

    actual_ts = get_filter_value_from_json(extractor.extract.call_args[0][0], filter_index=0)
    expected_ts = "{0}T00:00:00.000Z".format(namespace.begin_date[0])
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(extractor, EventTimestamp._term)


def test_when_not_given_begin_date_and_is_incremental_but_no_stored_checkpoint_exists_causes_exit(
    mocker, logger, namespace, extractor
):
    namespace.begin_date = None
    namespace.is_incremental = True
    mock_checkpoint = mocker.patch(
        "code42cli.securitydata.cursor_store.FileEventCursorStore.get_stored_insertion_timestamp"
    )
    mock_checkpoint.return_value = None
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_given_invalid_exposure_type_causes_exit(logger, namespace, extractor):
    namespace.exposure_types = [
        ExposureTypeOptions.APPLICATION_READ,
        "SomethingElseThatIsNotSupported",
        ExposureTypeOptions.IS_PUBLIC,
    ]
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_given_begin_date_with_len_3_causes_exit(logger, namespace, extractor):
    namespace.begin_date = (get_test_date_str(days_ago=5), "12:00:00", "+600")
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_given_end_date_with_len_3_causes_exit(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.end_date = (get_test_date_str(days_ago=5), "12:00:00", "+600")
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace_with_begin)


def test_extract_when_given_username_uses_username_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.c42usernames = ["test.testerson@example.com"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        DeviceUsername.is_in(namespace_with_begin.c42usernames)
    )


def test_extract_when_given_actor_uses_actor_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.actors = ["test.testerson"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(Actor.is_in(namespace_with_begin.actors))


def test_extract_when_given_md5_uses_md5_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.md5_hashes = ["098f6bcd4621d373cade4e832627b4f6"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(MD5.is_in(namespace_with_begin.md5_hashes))


def test_extract_when_given_sha256_uses_sha256_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.sha256_hashes = [
        "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    ]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        SHA256.is_in(namespace_with_begin.sha256_hashes)
    )


def test_extract_when_given_source_uses_source_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.sources = ["Gmail", "Yahoo"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(Source.is_in(namespace_with_begin.sources))


def test_extract_when_given_filename_uses_filename_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.filenames = ["file.txt", "txt.file"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FileName.is_in(namespace_with_begin.filenames)
    )


def test_extract_when_given_filepath_uses_filepath_filter(logger, namespace_with_begin, extractor):
    namespace_with_begin.filepaths = ["/path/to/file.txt", "path2"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(namespace_with_begin.filepaths)
    )


def test_extract_when_given_process_owner_uses_process_owner_filter(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.process_owners = ["test.testerson", "another"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        ProcessOwner.is_in(namespace_with_begin.process_owners)
    )


def test_extract_when_given_tab_url_uses_process_tab_url_filter(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.tab_urls = ["https://www.example.com"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        TabURL.is_in(namespace_with_begin.tab_urls)
    )


def test_extract_when_given_exposure_types_uses_exposure_type_is_in_filter(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.exposure_types = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        ExposureType.is_in(namespace_with_begin.exposure_types)
    )


def test_extract_when_given_include_non_exposure_does_not_include_exposure_type_exists(
    mocker, logger, namespace_with_begin, extractor
):
    namespace_with_begin.include_non_exposure_events = True
    ExposureType.exists = mocker.MagicMock()
    extraction_module.extract(logger, namespace_with_begin)
    assert not ExposureType.exists.call_count


def test_extract_when_not_given_include_non_exposure_includes_exposure_type_exists(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.include_non_exposure_events = False
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(ExposureType.exists())


def test_extract_when_given_multiple_search_args_uses_expected_filters(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.filepaths = ["/path/to/file.txt"]
    namespace_with_begin.process_owners = ["test.testerson", "flag.flagerson"]
    namespace_with_begin.tab_urls = ["https://www.example.com"]
    extraction_module.extract(logger, namespace_with_begin)
    assert str(extractor.extract.call_args[0][1]) == str(
        FilePath.is_in(namespace_with_begin.filepaths)
    )
    assert str(extractor.extract.call_args[0][2]) == str(
        ProcessOwner.is_in(namespace_with_begin.process_owners)
    )
    assert str(extractor.extract.call_args[0][3]) == str(
        TabURL.is_in(namespace_with_begin.tab_urls)
    )


def test_extract_when_given_include_non_exposure_and_exposure_types_causes_exit(
    logger, namespace_with_begin, extractor
):
    namespace_with_begin.exposure_types = ["ApplicationRead", "RemovableMedia", "CloudStorage"]
    namespace_with_begin.include_non_exposure_events = True
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace_with_begin)


def test_extract_when_creating_sdk_throws_causes_exit(logger, extractor, namespace, mock_42):
    def side_effect():
        raise Exception()

    mock_42.side_effect = side_effect
    with pytest.raises(SystemExit):
        extraction_module.extract(logger, namespace)


def test_extract_when_global_variable_is_true_and_is_interactive_prints_error(
    mocker, logger, namespace_with_begin, extractor
):
    mock_error_printer = mocker.patch("code42cli.securitydata.extraction.print_error")
    mock_is_interactive_function = mocker.patch("code42cli.securitydata.extraction.is_interactive")
    mock_is_interactive_function.return_value = True
    extraction_module._EXCEPTIONS_OCCURRED = True
    extraction_module.extract(logger, namespace_with_begin)
    assert mock_error_printer.call_count


def test_extract_when_global_variable_is_true_and_not_is_interactive_does_not_print_error(
    mocker, logger, namespace_with_begin, extractor
):
    mock_error_printer = mocker.patch("code42cli.securitydata.extraction.print_error")
    mock_is_interactive_function = mocker.patch("code42cli.securitydata.extraction.is_interactive")
    mock_is_interactive_function.return_value = False
    extraction_module._EXCEPTIONS_OCCURRED = True
    extraction_module.extract(logger, namespace_with_begin)
    assert not mock_error_printer.call_count


def test_extract_when_global_variable_is_false_and_is_interactive_does_not_print_error(
    mocker, logger, namespace_with_begin, extractor
):
    mock_error_printer = mocker.patch("code42cli.securitydata.extraction.print_error")
    mock_is_interactive_function = mocker.patch("code42cli.securitydata.extraction.is_interactive")
    mock_is_interactive_function.return_value = True
    extraction_module._EXCEPTIONS_OCCURRED = False
    extraction_module.extract(logger, namespace_with_begin)
    assert not mock_error_printer.call_count


def test_when_sdk_raises_exception_global_variable_gets_set(
    mocker, logger, namespace_with_begin, mock_42
):
    extraction_module._EXCEPTIONS_OCCURRED = False
    mock_sdk = mocker.MagicMock()

    # For ease
    mock = mocker.patch("code42cli.securitydata.extraction.is_interactive")
    mock.return_value = False

    def sdk_side_effect(self, *args):
        raise Exception()

    mock_sdk.security.search_file_events.side_effect = sdk_side_effect
    mock_42.return_value = mock_sdk

    mocker.patch(
        "c42eventextractor.extractors.FileEventExtractor._verify_compatibility_of_filter_groups"
    )

    extraction_module.extract(logger, namespace_with_begin)
    assert extraction_module._EXCEPTIONS_OCCURRED
