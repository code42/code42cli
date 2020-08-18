import json
import logging

import py42.sdk.queries.fileevents.filters as f
import pytest
from c42eventextractor.extractors import FileEventExtractor
from c42eventextractor.maps import FILE_EVENT_TO_SIGNATURE_ID_MAP
from py42.sdk.queries.fileevents.file_event_query import FileEventQuery
from tests.cmds.conftest import filter_term_is_in_call_args
from tests.cmds.conftest import get_filter_value_from_json
from tests.conftest import get_test_date_str

from code42cli import errors
from code42cli import PRODUCT_NAME
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.cmds.securitydata import file_events_output_format
from code42cli.cmds.securitydata import to_cef
from code42cli.main import cli
from code42cli.output_formats import to_dynamic_csv
from code42cli.output_formats import to_formatted_json
from code42cli.output_formats import to_json

BEGIN_TIMESTAMP = 1577858400.0
END_TIMESTAMP = 1580450400.0
CURSOR_TIMESTAMP = 1579500000.0


TEST_LIST_RESPONSE = {
    "searches": [
        {
            "id": "a083f08d-8f33-4cbd-81c4-8d1820b61185",
            "name": "test-events",
            "notes": "py42 is here",
        },
    ]
}

TEST_EMPTY_LIST_RESPONSE = {"searches": []}


@pytest.fixture
def file_event_extractor(mocker):
    mock = mocker.patch(
        "{}.cmds.securitydata._get_file_event_extractor".format(PRODUCT_NAME)
    )
    mock.return_value = mocker.MagicMock(spec=FileEventExtractor)
    return mock.return_value


@pytest.fixture
def file_event_cursor_with_checkpoint(mocker):
    mock = mocker.patch(
        "{}.cmds.securitydata._get_file_event_cursor_store".format(PRODUCT_NAME)
    )
    mock_cursor = mocker.MagicMock(spec=FileEventCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    mock.expected_timestamp = "2020-01-20T06:00:00+00:00"
    return mock


@pytest.fixture
def file_event_cursor_without_checkpoint(mocker):
    mock = mocker.patch(
        "{}.cmds.securitydata._get_file_event_cursor_store".format(PRODUCT_NAME)
    )
    mock_cursor = mocker.MagicMock(spec=FileEventCursorStore)
    mock_cursor.get.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch(
        "{}.cmds.search.options.parse_min_timestamp".format(PRODUCT_NAME)
    )
    mock.return_value = BEGIN_TIMESTAMP
    mock.expected_timestamp = "2020-01-01T06:00:00.000Z"
    return mock


@pytest.fixture
def mock_file_event_log_record():
    return [AED_EVENT_DICT]


AED_CLOUD_ACTIVITY_EVENT_DICT = json.loads(
    """{
    "url": "https://www.example.com",
    "syncDestination": "TEST_SYNC_DESTINATION",
    "sharedWith": [{"cloudUsername": "example1@example.com"}, {"cloudUsername": "example2@example.com"}],
    "cloudDriveId": "TEST_CLOUD_DRIVE_ID",
    "actor": "actor@example.com",
    "tabUrl": "TEST_TAB_URL",
    "windowTitle": "TEST_WINDOW_TITLE"
    }"""
)


AED_REMOVABLE_MEDIA_EVENT_DICT = json.loads(
    """{
    "removableMediaVendor": "TEST_VENDOR_NAME",
    "removableMediaName": "TEST_NAME",
    "removableMediaSerialNumber": "TEST_SERIAL_NUMBER",
    "removableMediaCapacity": 5000000,
    "removableMediaBusType": "TEST_BUS_TYPE"
    }"""
)

AED_EMAIL_EVENT_DICT = json.loads(
    """{
    "emailSender": "TEST_EMAIL_SENDER",
    "emailRecipients": ["test.recipient1@example.com", "test.recipient2@example.com"]
    }"""
)


AED_EVENT_DICT = json.loads(
    """{
    "eventId": "0_1d71796f-af5b-4231-9d8e-df6434da4663_912339407325443353_918253081700247636_16",
    "eventType": "READ_BY_APP",
    "eventTimestamp": "2019-09-09T02:42:23.851Z",
    "insertionTimestamp": "2019-09-09T22:47:42.724Z",
    "filePath": "/Users/testtesterson/Downloads/About Downloads.lpdf/Contents/Resources/English.lproj/",
    "fileName": "InfoPlist.strings",
    "fileType": "FILE",
    "fileCategory": "UNCATEGORIZED",
    "fileSize": 86,
    "fileOwner": "testtesterson",
    "md5Checksum": "19b92e63beb08c27ab4489fcfefbbe44",
    "sha256Checksum": "2e0677355c37fa18fd20d372c7420b8b34de150c5801910c3bbb1e8e04c727ef",
    "createTimestamp": "2012-07-22T02:19:29Z",
    "modifyTimestamp": "2012-12-19T03:00:08Z",
    "deviceUserName": "test.testerson+testair@code42.com",
    "osHostName": "Test's MacBook Air",
    "domainName": "192.168.0.3",
    "publicIpAddress": "71.34.4.22",
    "privateIpAddresses": [
        "fe80:0:0:0:f053:a9bd:973:6c8c%utun1",
        "fe80:0:0:0:a254:cb31:8840:9d6b%utun0",
        "0:0:0:0:0:0:0:1%lo0",
        "192.168.0.3",
        "fe80:0:0:0:0:0:0:1%lo0",
        "fe80:0:0:0:8c28:1ac9:5745:a6e7%utun3",
        "fe80:0:0:0:2e4a:351c:bb9b:2f28%utun2",
        "fe80:0:0:0:6df:855c:9436:37f8%utun4",
        "fe80:0:0:0:ce:5072:e5f:7155%en0",
        "fe80:0:0:0:b867:afff:fefc:1a82%awdl0",
        "127.0.0.1"
    ],
    "deviceUid": "912339407325443353",
    "userUid": "912338501981077099",
    "actor": null,
    "directoryId": [],
    "source": "Endpoint",
    "url": null,
    "shared": null,
    "sharedWith": [],
    "sharingTypeAdded": [],
    "cloudDriveId": null,
    "detectionSourceAlias": null,
    "fileId": null,
    "exposure": [
        "ApplicationRead"
    ],
    "processOwner": "testtesterson",
    "processName": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "removableMediaVendor": null,
    "removableMediaName": null,
    "removableMediaSerialNumber": null,
    "removableMediaCapacity": null,
    "removableMediaBusType": null,
    "syncDestination": null
    }"""
)


@pytest.fixture
def mock_file_event_removable_media_event_log_record():
    return [AED_REMOVABLE_MEDIA_EVENT_DICT]


@pytest.fixture
def mock_file_event_cloud_activity_event_log_record():
    return [AED_CLOUD_ACTIVITY_EVENT_DICT]


@pytest.fixture
def mock_file_event_email_event_log_record():
    return [AED_EMAIL_EVENT_DICT]


ADVANCED_QUERY_JSON = '{"some": "complex json"}'


def test_search_when_is_advanced_query_uses_only_the_extract_advanced_method(
    runner, cli_state, file_event_extractor
):
    runner.invoke(
        cli,
        ["security-data", "search", "--advanced-query", ADVANCED_QUERY_JSON],
        obj=cli_state,
    )
    file_event_extractor.extract_advanced.assert_called_once_with(
        '{"some": "complex json"}'
    )
    assert file_event_extractor.extract.call_count == 0
    assert file_event_extractor.extract_advanced.call_count == 1


def test_search_when_is_not_advanced_query_uses_only_the_extract_advanced_method(
    runner, cli_state, file_event_extractor
):
    runner.invoke(cli, ["security-data", "search", "--begin", "1d"], obj=cli_state)
    assert file_event_extractor.extract_advanced.call_count == 0
    assert file_event_extractor.extract.call_count == 1


@pytest.mark.parametrize(
    "arg",
    [
        ("--begin", "1d"),
        ("--end", "1d"),
        ("--c42-username", "test@code42.com"),
        ("--actor", "test.testerson"),
        ("--md5", "abcd1234"),
        ("--sha256", "abcdefg12345678"),
        ("--source", "Gmail"),
        ("--file-name", "test.txt"),
        ("--file-path", "C:\\Program Files"),
        ("--process-owner", "root"),
        ("--tab-url", "https://example.com"),
        ("--type", "SharedViaLink"),
        ("--include-non-exposure",),
        ("--use-checkpoint", "test"),
    ],
)
def test_search_with_advanced_query_and_incompatible_argument_errors(
    runner, arg, cli_state
):
    result = runner.invoke(
        cli,
        ["security-data", "search", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@pytest.mark.parametrize(
    "arg",
    [
        ("--begin", "1d"),
        ("--end", "1d"),
        ("--c42-username", "test@code42.com"),
        ("--actor", "test.testerson"),
        ("--md5", "abcd1234"),
        ("--sha256", "abcdefg12345678"),
        ("--source", "Gmail"),
        ("--file-name", "test.txt"),
        ("--file-path", "C:\\Program Files"),
        ("--process-owner", "root"),
        ("--tab-url", "https://example.com"),
        ("--type", "SharedViaLink"),
        ("--include-non-exposure",),
        ("--use-checkpoint", "test"),
    ],
)
def test_search_with_saved_search_and_incompatible_argument_errors(
    runner, arg, cli_state
):
    result = runner.invoke(
        cli,
        ["security-data", "search", "--saved-search", "test_id", *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --saved-search".format(arg[0]) in result.output


def test_search_when_given_begin_and_end_dates_uses_expected_query(
    runner, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", begin_date, "--end", end_date],
        obj=cli_state,
    )
    filters = file_event_extractor.extract.call_args[0][1]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{}T00:00:00.000Z".format(begin_date)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{}T23:59:59.999Z".format(end_date)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


def test_search_when_given_begin_and_end_date_and_time_uses_expected_query(
    runner, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33:02"
    runner.invoke(
        cli,
        [
            "security-data",
            "search",
            "--begin",
            "{} {}".format(begin_date, time),
            "--end",
            "{} {}".format(end_date, time),
        ],
        obj=cli_state,
    )
    filters = file_event_extractor.extract.call_args[0][1]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{}T{}.000Z".format(begin_date, time)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{}T{}.000Z".format(end_date, time)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


def test_search_when_given_begin_date_and_time_without_seconds_uses_expected_query(
    runner, cli_state, file_event_extractor
):
    date = get_test_date_str(days_ago=89)
    time = "15:33"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "{} {}".format(date, time)],
        obj=cli_state,
    )
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][1], filter_index=0
    )
    expected = "{}T{}:00.000Z".format(date, time)
    assert actual == expected


def test_search_when_given_end_date_and_time_uses_expected_query(
    runner, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=10)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33"
    runner.invoke(
        cli,
        [
            "security-data",
            "search",
            "--begin",
            begin_date,
            "--end",
            "{} {}".format(end_date, time),
        ],
        obj=cli_state,
    )
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][1], filter_index=1
    )
    expected = "{}T{}:00.000Z".format(end_date, time)
    assert actual == expected


def test_search_when_given_begin_date_more_than_ninety_days_back_errors(
    runner, cli_state,
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    result = runner.invoke(
        cli, ["security-data", "search", "--begin", begin_date], obj=cli_state
    )
    assert result.exit_code == 2
    assert "must be within 90 days" in result.output


def test_search_when_given_begin_date_past_90_days_and_use_checkpoint_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    runner, cli_state, file_event_cursor_with_checkpoint, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", begin_date, "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert not filter_term_is_in_call_args(
        file_event_extractor, f.InsertionTimestamp._term
    )


def test_search_when_given_begin_date_and_not_use_checkpoint_and_cursor_exists_uses_begin_date(
    runner, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=1)
    runner.invoke(
        cli, ["security-data", "search", "--begin", begin_date], obj=cli_state
    )
    actual_ts = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][1], filter_index=0
    )
    expected_ts = "{}T00:00:00.000Z".format(begin_date)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(file_event_extractor, f.EventTimestamp._term)


def test_search_when_end_date_is_before_begin_date_causes_exit(runner, cli_state):
    begin_date = get_test_date_str(days_ago=1)
    end_date = get_test_date_str(days_ago=3)
    result = runner.invoke(
        cli,
        ["security-data", "search", "--begin", begin_date, "--end", end_date],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "'--begin': cannot be after --end date" in result.output


def test_search_with_only_begin_calls_extract_with_expected_args(
    runner, cli_state, file_event_extractor, begin_option
):
    result = runner.invoke(
        cli, ["security-data", "search", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    assert str(
        file_event_extractor.extract.call_args[0][1]
    ) == '{{"filterClause":"AND", "filters":[{{"operator":"ON_OR_AFTER", "term":"eventTimestamp", "value":"{}"}}]}}'.format(
        begin_option.expected_timestamp
    )


def test_search_with_use_checkpoint_and_without_begin_and_without_checkpoint_causes_expected_error(
    runner, cli_state, file_event_cursor_without_checkpoint
):
    result = runner.invoke(
        cli, ["security-data", "search", "--use-checkpoint", "test"], obj=cli_state
    )
    assert result.exit_code == 2
    assert (
        "--begin date is required for --use-checkpoint when no checkpoint exists yet."
        in result.output
    )


def test_search_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    runner,
    cli_state,
    file_event_extractor,
    begin_option,
    file_event_cursor_without_checkpoint,
):
    result = runner.invoke(
        cli,
        ["security-data", "search", "--use-checkpoint", "test", "--begin", "1h"],
        obj=cli_state,
    )
    assert result.exit_code == 0
    assert len(file_event_extractor.extract.call_args[0]) == 2
    assert begin_option.expected_timestamp in str(
        file_event_extractor.extract.call_args[0][1]
    )


def test_search_with_use_checkpoint_and_with_begin_and_with_stored_checkpoint_calls_extract_with_checkpoint_and_ignores_begin_arg(
    runner, cli_state, file_event_extractor, file_event_cursor_with_checkpoint,
):
    result = runner.invoke(
        cli,
        ["security-data", "search", "--use-checkpoint", "test", "--begin", "1h"],
        obj=cli_state,
    )
    assert result.exit_code == 0
    assert len(file_event_extractor.extract.call_args[0]) == 1
    assert (
        "checkpoint of {} exists".format(
            file_event_cursor_with_checkpoint.expected_timestamp
        )
        in result.output
    )


def test_search_when_given_invalid_exposure_type_causes_exit(runner, cli_state):
    result = runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1d", "-t", "NotValid"],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "invalid choice: NotValid" in result.output


def test_search_when_given_username_uses_username_filter(
    runner, cli_state, file_event_extractor
):
    c42_username = "test@code42.com"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--c42-username", c42_username],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.DeviceUsername.is_in([c42_username])) in filter_strings


def test_search_when_given_actor_is_uses_username_filter(
    runner, cli_state, file_event_extractor
):
    actor_name = "test.testerson"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--actor", actor_name],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.Actor.is_in([actor_name])) in filter_strings


def test_search_when_given_md5_uses_md5_filter(runner, cli_state, file_event_extractor):
    md5 = "abcd12345"
    runner.invoke(
        cli, ["security-data", "search", "--begin", "1h", "--md5", md5], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.MD5.is_in([md5])) in filter_strings


def test_search_when_given_sha256_uses_sha256_filter(
    runner, cli_state, file_event_extractor
):
    sha_256 = "abcd12345"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--sha256", sha_256],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.SHA256.is_in([sha_256])) in filter_strings


def test_search_when_given_source_uses_source_filter(
    runner, cli_state, file_event_extractor
):
    source = "Gmail"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--source", source],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.Source.is_in([source])) in filter_strings


def test_search_when_given_file_name_uses_file_name_filter(
    runner, cli_state, file_event_extractor
):
    filename = "test.txt"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--file-name", filename],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.FileName.is_in([filename])) in filter_strings


def test_search_when_given_file_path_uses_file_path_filter(
    runner, cli_state, file_event_extractor
):
    filepath = "C:\\Program Files"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--file-path", filepath],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.FilePath.is_in([filepath])) in filter_strings


def test_when_given_process_owner_uses_process_owner_filter(
    runner, cli_state, file_event_extractor
):
    process_owner = "root"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--process-owner", process_owner],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.ProcessOwner.is_in([process_owner])) in filter_strings


def test_when_given_tab_url_uses_process_tab_url_filter(
    runner, cli_state, file_event_extractor
):
    tab_url = "https://example.com"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--tab-url", tab_url],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.TabURL.is_in([tab_url])) in filter_strings


def test_when_given_exposure_types_uses_exposure_type_is_in_filter(
    runner, cli_state, file_event_extractor
):
    exposure_type = "SharedViaLink"
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--type", exposure_type],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.ExposureType.is_in([exposure_type])) in filter_strings


def test_when_given_include_non_exposure_does_not_include_exposure_type_exists(
    runner, cli_state, file_event_extractor
):
    runner.invoke(
        cli,
        ["security-data", "search", "--begin", "1h", "--include-non-exposure"],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.ExposureType.exists()) not in filter_strings


def test_when_not_given_include_non_exposure_includes_exposure_type_exists(
    runner, cli_state, file_event_extractor
):
    runner.invoke(
        cli, ["security-data", "search", "--begin", "1h"], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.ExposureType.exists()) in filter_strings


def test_when_given_multiple_search_args_uses_expected_filters(
    runner, cli_state, file_event_extractor
):
    process_owner = "root"
    c42_username = "test@code42.com"
    filename = "test.txt"
    runner.invoke(
        cli,
        [
            "security-data",
            "search",
            "--begin",
            "1h",
            "--process-owner",
            process_owner,
            "--c42-username",
            c42_username,
            "--file-name",
            filename,
        ],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(f.ProcessOwner.is_in([process_owner])) in filter_strings
    assert str(f.FileName.is_in([filename])) in filter_strings
    assert str(f.DeviceUsername.is_in([c42_username])) in filter_strings


def test_when_given_include_non_exposure_and_exposure_types_causes_exit(
    runner, cli_state, file_event_extractor
):
    result = runner.invoke(
        cli,
        [
            "security-data",
            "search",
            "--begin",
            "1h",
            "--include-non-exposure",
            "--type",
            "SharedViaLink",
        ],
        obj=cli_state,
    )
    assert result.exit_code == 2


def test_when_extraction_handles_error_expected_message_logged_and_printed_and_global_errored_flag_set(
    runner, cli_state, caplog
):
    errors.ERRORED = False
    exception_msg = "Test Exception"

    def file_search_error(x):
        raise Exception(exception_msg)

    cli_state.sdk.securitydata.search_file_events.side_effect = file_search_error
    with caplog.at_level(logging.ERROR):
        result = runner.invoke(
            cli, ["security-data", "search", "--begin", "1d"], obj=cli_state
        )
        assert exception_msg in result.output
        assert exception_msg in caplog.text
        assert errors.ERRORED


def test_saved_search_calls_extractor_extract_and_saved_search_execute(
    runner, cli_state, file_event_extractor
):
    search_query = {
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "operator": "ON_OR_AFTER",
                        "term": "eventTimestamp",
                        "value": "2020-05-01T00:00:00.000Z",
                    }
                ],
            },
            {
                "filterClause": "OR",
                "filters": [
                    {"operator": "IS", "term": "eventType", "value": "DELETED"},
                    {"operator": "IS", "term": "eventType", "value": "EMAILED"},
                    {"operator": "IS", "term": "eventType", "value": "MODIFIED"},
                    {"operator": "IS", "term": "eventType", "value": "READ_BY_AP"},
                    {"operator": "IS", "term": "eventType", "value": "CREATED"},
                ],
            },
        ],
        "pgNum": 1,
        "pgSize": 10000,
        "srtDir": "asc",
        "srtKey": "eventId",
    }
    query = FileEventQuery.from_dict(search_query)
    cli_state.sdk.securitydata.savedsearches.get_query.return_value = query
    runner.invoke(
        cli, ["security-data", "search", "--saved-search", "test_id"], obj=cli_state
    )
    assert file_event_extractor.extract.call_count == 1
    assert str(file_event_extractor.extract.call_args[0][0]) in str(query)
    assert str(file_event_extractor.extract.call_args[0][1]) in str(query)


def test_saved_search_list_calls_get_method(runner, cli_state):
    runner.invoke(cli, ["security-data", "saved-search", "list"], obj=cli_state)
    assert cli_state.sdk.securitydata.savedsearches.get.call_count == 1


def test_show_detail_calls_get_by_id_method(runner, cli_state):
    test_id = "test_id"
    runner.invoke(
        cli, ["security-data", "saved-search", "show", test_id], obj=cli_state
    )
    cli_state.sdk.securitydata.savedsearches.get_by_id.assert_called_once_with(test_id)


def test_search_with_or_query_flag_produces_expected_query(runner, cli_state):
    begin_date = get_test_date_str(days_ago=10)
    test_username = "test@example.com"
    test_filename = "test.txt"
    runner.invoke(
        cli,
        [
            "security-data",
            "search",
            "--or-query",
            "--begin",
            begin_date,
            "--c42-username",
            test_username,
            "--file-name",
            test_filename,
        ],
        obj=cli_state,
    )
    expected_query = {
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {"operator": "EXISTS", "term": "exposure", "value": None},
                    {
                        "operator": "ON_OR_AFTER",
                        "term": "eventTimestamp",
                        "value": "{}T00:00:00.000Z".format(begin_date),
                    },
                ],
            },
            {
                "filterClause": "OR",
                "filters": [
                    {
                        "operator": "IS",
                        "term": "deviceUserName",
                        "value": "test@example.com",
                    },
                    {"operator": "IS", "term": "fileName", "value": "test.txt"},
                ],
            },
        ],
        "pgNum": 1,
        "pgSize": 10000,
        "srtDir": "asc",
        "srtKey": "insertionTimestamp",
    }
    actual_query = json.loads(
        str(cli_state.sdk.securitydata.search_file_events.call_args[0][0])
    )
    assert actual_query == expected_query


def test_saved_search_list_with_format_option_returns_csv_formatted_response(
    runner, cli_state
):
    cli_state.sdk.securitydata.savedsearches.get.return_value = TEST_LIST_RESPONSE
    result = runner.invoke(
        cli, ["security-data", "saved-search", "list", "-f", "csv"], obj=cli_state
    )
    assert "Name,Id" in result.output
    assert "test-events,a083f08d-8f33-4cbd-81c4-8d1820b61185" in result.output


def test_saved_search_list_with_format_option_does_not_return_when_response_is_empty(
    runner, cli_state
):
    cli_state.sdk.securitydata.savedsearches.get.return_value = TEST_EMPTY_LIST_RESPONSE
    result = runner.invoke(
        cli, ["security-data", "saved-search", "list", "-f", "csv"], obj=cli_state
    )
    assert "Name,Id" not in result.output


def test_file_events_output_format_returns_to_dynamic_csv_function_when_csv_option_is_passed():
    extraction_output_format_function = file_events_output_format(None, None, "CSV")
    assert id(extraction_output_format_function) == id(to_dynamic_csv)


def test_file_events_output_format_returns_to_formatted_json_function_when_json__option_is_passed():
    format_function = file_events_output_format(None, None, "JSON")
    assert id(format_function) == id(to_formatted_json)


def test_file_events_output_format_returns_to_json_function_when_raw_json_format_option_is_passed():
    format_function = file_events_output_format(None, None, "RAW-JSON")
    assert id(format_function) == id(to_json)


def test_file_events_output_format_returns_to_cef_function_when_cef_format_option_is_passed():
    format_function = file_events_output_format(None, None, "CEF")
    assert id(format_function) == id(to_cef)


def test_to_cef_returns_cef_tagged_string(mock_file_event_log_record):
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[0] == "CEF:0"


def test_to_cef_uses_correct_vendor_name(mock_file_event_log_record):
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[1] == "Code42"


def test_to_cef_uses_correct_default_product_name(mock_file_event_log_record):
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[2] == "Advanced Exfiltration Detection"


def test_to_cef_uses_correct_default_severity(mock_file_event_log_record):
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[6] == "5"


def test_to_cef_excludes_none_values_from_output(mock_file_event_log_record):
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    assert "=None " not in cef_parts[-1]


def test_to_cef_excludes_empty_values_from_output(mock_file_event_log_record):
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    assert "= " not in cef_parts[-1]


def test_to_cef_excludes_file_event_fields_not_in_cef_map(mock_file_event_log_record):
    test_value = "definitelyExcludedValue"
    mock_file_event_log_record[0]["unmappedFieldName"] = test_value
    cef_out = to_cef(mock_file_event_log_record, None)
    cef_parts = get_cef_parts(cef_out)
    del mock_file_event_log_record[0]["unmappedFieldName"]
    assert test_value not in cef_parts[-1]


def test_to_cef_includes_os_hostname_if_present(mock_file_event_log_record):
    expected_field_name = "shost"
    expected_value = "Test's MacBook Air"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_public_ip_address_if_present(mock_file_event_log_record):
    expected_field_name = "src"
    expected_value = "71.34.4.22"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_user_uid_if_present(mock_file_event_log_record):
    expected_field_name = "suid"
    expected_value = "912338501981077099"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_device_username_if_present(mock_file_event_log_record):
    expected_field_name = "suser"
    expected_value = "test.testerson+testair@code42.com"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_capacity_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cn1"
    expected_value = "5000000"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_capacity_label_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cn1Label"
    expected_value = "Code42AEDRemovableMediaCapacity"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_bus_type_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs1"
    expected_value = "TEST_BUS_TYPE"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_bus_type_label_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs1Label"
    expected_value = "Code42AEDRemovableMediaBusType"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_vendor_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs2"
    expected_value = "TEST_VENDOR_NAME"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_vendor_label_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs2Label"
    expected_value = "Code42AEDRemovableMediaVendor"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_name_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs3"
    expected_value = "TEST_NAME"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_name_label_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs3Label"
    expected_value = "Code42AEDRemovableMediaName"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_serial_number_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs4"
    expected_value = "TEST_SERIAL_NUMBER"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_serial_number_label_if_present(
    mock_file_event_removable_media_event_log_record,
):
    expected_field_name = "cs4Label"
    expected_value = "Code42AEDRemovableMediaSerialNumber"
    cef_out = to_cef(mock_file_event_removable_media_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_actor_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "suser"
    expected_value = "actor@example.com"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_sync_destination_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "destinationServiceName"
    expected_value = "TEST_SYNC_DESTINATION"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_event_timestamp_if_present(mock_file_event_log_record):
    expected_field_name = "end"
    expected_value = "1567996943851"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_create_timestamp_if_present(mock_file_event_log_record):
    expected_field_name = "fileCreateTime"
    expected_value = "1342923569000"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_md5_checksum_if_present(mock_file_event_log_record):
    expected_field_name = "fileHash"
    expected_value = "19b92e63beb08c27ab4489fcfefbbe44"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_modify_timestamp_if_present(mock_file_event_log_record):
    expected_field_name = "fileModificationTime"
    expected_value = "1355886008000"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_path_if_present(mock_file_event_log_record):
    expected_field_name = "filePath"
    expected_value = "/Users/testtesterson/Downloads/About Downloads.lpdf/Contents/Resources/English.lproj/"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_name_if_present(mock_file_event_log_record):
    expected_field_name = "fname"
    expected_value = "InfoPlist.strings"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_size_if_present(mock_file_event_log_record):
    expected_field_name = "fsize"
    expected_value = "86"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_category_if_present(mock_file_event_log_record):
    expected_field_name = "fileType"
    expected_value = "UNCATEGORIZED"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_exposure_if_present(mock_file_event_log_record):
    expected_field_name = "reason"
    expected_value = "ApplicationRead"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_url_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "filePath"
    expected_value = "https://www.example.com"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_insertion_timestamp_if_present(mock_file_event_log_record):
    expected_field_name = "rt"
    expected_value = "1568069262724"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_process_name_if_present(mock_file_event_log_record):
    expected_field_name = "sproc"
    expected_value = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_event_id_if_present(mock_file_event_log_record):
    expected_field_name = "externalId"
    expected_value = "0_1d71796f-af5b-4231-9d8e-df6434da4663_912339407325443353_918253081700247636_16"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_device_uid_if_present(mock_file_event_log_record):
    expected_field_name = "deviceExternalId"
    expected_value = "912339407325443353"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_domain_name_if_present(mock_file_event_log_record):
    expected_field_name = "dvchost"
    expected_value = "192.168.0.3"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_source_if_present(mock_file_event_log_record):
    expected_field_name = "sourceServiceName"
    expected_value = "Endpoint"
    cef_out = to_cef(mock_file_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_cloud_drive_id_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "aid"
    expected_value = "TEST_CLOUD_DRIVE_ID"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_shared_with_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "duser"
    expected_value = "example1@example.com,example2@example.com"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_tab_url_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "request"
    expected_value = "TEST_TAB_URL"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_window_title_if_present(
    mock_file_event_cloud_activity_event_log_record,
):
    expected_field_name = "requestClientApplication"
    expected_value = "TEST_WINDOW_TITLE"
    cef_out = to_cef(mock_file_event_cloud_activity_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_email_recipients_if_present(
    mock_file_event_email_event_log_record,
):
    expected_field_name = "duser"
    expected_value = "test.recipient1@example.com,test.recipient2@example.com"
    cef_out = to_cef(mock_file_event_email_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_email_sender_if_present(
    mock_file_event_email_event_log_record,
):
    expected_field_name = "suser"
    expected_value = "TEST_EMAIL_SENDER"
    cef_out = to_cef(mock_file_event_email_event_log_record, None)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_created(
    mock_file_event_log_record,
):
    event_type = "CREATED"
    mock_file_event_log_record[0]["eventType"] = event_type
    cef_out = to_cef(mock_file_event_log_record, None)
    assert event_name_assigned_correct_signature_id(event_type, "C42200", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_modified(
    mock_file_event_log_record,
):
    event_type = "MODIFIED"
    mock_file_event_log_record[0]["eventType"] = event_type
    cef_out = to_cef(mock_file_event_log_record, None)
    assert event_name_assigned_correct_signature_id(event_type, "C42201", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_deleted(
    mock_file_event_log_record,
):
    event_type = "DELETED"
    mock_file_event_log_record[0]["eventType"] = event_type
    cef_out = to_cef(mock_file_event_log_record, None)
    assert event_name_assigned_correct_signature_id(event_type, "C42202", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_read_by_app(
    mock_file_event_log_record,
):
    event_type = "READ_BY_APP"
    mock_file_event_log_record[0]["eventType"] = event_type
    cef_out = to_cef(mock_file_event_log_record, None)
    assert event_name_assigned_correct_signature_id(event_type, "C42203", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_emailed(
    mock_file_event_email_event_log_record,
):
    event_type = "EMAILED"
    mock_file_event_email_event_log_record[0]["eventType"] = event_type
    cef_out = to_cef(mock_file_event_email_event_log_record, None)
    assert event_name_assigned_correct_signature_id(event_type, "C42204", cef_out)


def get_cef_parts(cef_str):
    return cef_str[0].split("|")


def key_value_pair_in_cef_extension(field_name, field_value, cef_str):
    cef_parts = get_cef_parts(cef_str)
    kvp = "{}={}".format(field_name, field_value)
    return kvp in cef_parts[-1]


def event_name_assigned_correct_signature_id(event_name, signature_id, cef_out):
    if event_name in FILE_EVENT_TO_SIGNATURE_ID_MAP:
        cef_parts = get_cef_parts(cef_out)
        return cef_parts[4] == signature_id and cef_parts[5] == event_name

    return False
