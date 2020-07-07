import logging

import pytest
from c42eventextractor.extractors import FileEventExtractor
from py42.sdk.queries.fileevents.file_event_query import FileEventQuery
from py42.sdk.queries.fileevents.filters import *

from code42cli import PRODUCT_NAME, errors
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.main import cli
from tests.cmds.conftest import get_filter_value_from_json, filter_term_is_in_call_args
from tests.conftest import get_test_date_str

BEGIN_TIMESTAMP = 1577858400.0
END_TIMESTAMP = 1580450400.0
CURSOR_TIMESTAMP = 1579500000.0


@pytest.fixture
def file_event_extractor(mocker):
    mock = mocker.patch("{}.cmds.securitydata._get_file_event_extractor".format(PRODUCT_NAME))
    mock.return_value = mocker.MagicMock(spec=FileEventExtractor)
    return mock.return_value


@pytest.fixture
def file_event_cursor_with_checkpoint(mocker):
    mock = mocker.patch("{}.cmds.securitydata._get_file_event_cursor_store".format(PRODUCT_NAME))
    mock_cursor = mocker.MagicMock(spec=FileEventCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def file_event_cursor_without_checkpoint(mocker):
    mock = mocker.patch("{}.cmds.securitydata._get_file_event_cursor_store".format(PRODUCT_NAME))
    mock_cursor = mocker.MagicMock(spec=FileEventCursorStore)
    mock_cursor.get.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def file_event_extract_func(mocker):
    return mocker.patch("{}.cmds.securitydata._extract".format(PRODUCT_NAME))


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch("{}.cmds.search.options.parse_min_timestamp".format(PRODUCT_NAME))
    mock.return_value = BEGIN_TIMESTAMP
    return mock


ADVANCED_QUERY_JSON = '{"some": "complex json"}'


parametrize_search_output_cmds = pytest.mark.parametrize(
    "cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]]
)

parametrize_incompatible_args = pytest.mark.parametrize(
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


@parametrize_search_output_cmds
def test_when_is_advanced_query_uses_only_the_extract_advanced_method(
    runner, cmd, cli_state, file_event_extractor
):
    result = runner.invoke(
        cli, ["security-data", *cmd, "--advanced-query", ADVANCED_QUERY_JSON], obj=cli_state
    )
    file_event_extractor.extract_advanced.assert_called_once_with('{"some": "complex json"}')
    assert file_event_extractor.extract.call_count == 0
    assert file_event_extractor.extract_advanced.call_count == 1


@parametrize_search_output_cmds
def test_when_is_advanced_query_uses_only_the_extract_advanced_method(
    runner, cmd, cli_state, file_event_extractor
):
    result = runner.invoke(cli, ["security-data", *cmd, "--begin", "1d"], obj=cli_state)
    assert file_event_extractor.extract_advanced.call_count == 0
    assert file_event_extractor.extract.call_count == 1


@parametrize_incompatible_args
def test_print_when_advanced_query_and_other_incompatible_argument_passed(runner, arg, cli_state):
    result = runner.invoke(
        cli,
        ["security-data", "print", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@parametrize_incompatible_args
def test_print_when_saved_search_and_other_incompatible_argument_passed(runner, arg, cli_state):
    result = runner.invoke(
        cli, ["security-data", "print", "--saved-search", "test_id", *arg], obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --saved-search".format(arg[0]) in result.output


@parametrize_incompatible_args
def test_write_to_when_advanced_query_and_other_incompatible_argument_passed(
    runner, arg, cli_state
):
    result = runner.invoke(
        cli,
        ["security-data", "write-to", "test_file", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@parametrize_incompatible_args
def test_write_to_when_saved_search_and_other_incompatible_argument_passed(runner, arg, cli_state):
    result = runner.invoke(
        cli,
        ["security-data", "write-to", "test_file", "--saved-search", "test_id", *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --saved-search".format(arg[0]) in result.output


@parametrize_incompatible_args
def test_send_to_when_advanced_query_and_other_incompatible_argument_passed(runner, arg, cli_state):
    result = runner.invoke(
        cli,
        ["security-data", "send-to", "localhost", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@parametrize_incompatible_args
def test_send_to_when_saved_search_and_other_incompatible_argument_passed(runner, arg, cli_state):
    result = runner.invoke(
        cli,
        ["security-data", "send-to", "localhost", "--saved-search", "test_id", *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --saved-search".format(arg[0]) in result.output


@parametrize_search_output_cmds
def test_when_given_begin_and_end_dates_uses_expected_query(
    runner, cmd, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    result = runner.invoke(
        cli, ["security-data", "print", "--begin", begin_date, "--end", end_date], obj=cli_state
    )
    filters = file_event_extractor.extract.call_args[0][1]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{0}T00:00:00.000Z".format(begin_date)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{0}T23:59:59.999Z".format(end_date)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@parametrize_search_output_cmds
def test_when_given_begin_and_end_date_and_time_uses_expected_query(
    runner, cmd, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33:02"
    result = runner.invoke(
        cli,
        [
            "security-data",
            "print",
            "--begin",
            "{} {}".format(begin_date, time),
            "--end",
            "{} {}".format(end_date, time),
        ],
        obj=cli_state,
    )
    filters = file_event_extractor.extract.call_args[0][1]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{0}T{1}.000Z".format(begin_date, time)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{0}T{1}.000Z".format(end_date, time)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@parametrize_search_output_cmds
def test_when_given_begin_date_and_time_without_seconds_uses_expected_query(
    runner, cmd, cli_state, file_event_extractor
):
    date = get_test_date_str(days_ago=89)
    time = "15:33"
    result = runner.invoke(
        cli, ["security-data", "print", "--begin", "{} {}".format(date, time)], obj=cli_state
    )
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][1], filter_index=0
    )
    expected = "{0}T{1}:00.000Z".format(date, time)
    assert actual == expected


@parametrize_search_output_cmds
def test_when_given_end_date_and_time_uses_expected_query(
    runner, cmd, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=10)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33"
    result = runner.invoke(
        cli,
        ["security-data", "print", "--begin", begin_date, "--end", "{} {}".format(end_date, time)],
        obj=cli_state,
    )
    actual = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][1], filter_index=1
    )
    expected = "{0}T{1}:00.000Z".format(end_date, time)
    assert actual == expected


@parametrize_search_output_cmds
def test_when_given_begin_date_more_than_ninety_days_back_in_ad_hoc_mode_causes_exit(
    runner, cmd, cli_state,
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    result = runner.invoke(cli, ["security-data", *cmd, "--begin", begin_date], obj=cli_state)
    assert result.exit_code == 2
    assert "must be within 90 days" in result.output


@parametrize_search_output_cmds
def test_when_given_begin_date_past_90_days_and_use_checkpoint_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    runner, cmd, cli_state, file_event_cursor_with_checkpoint, mocker, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    result = runner.invoke(
        cli,
        ["security-data", *cmd, "--begin", begin_date, "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert not filter_term_is_in_call_args(file_event_extractor, InsertionTimestamp._term)


@parametrize_search_output_cmds
def test_when_given_begin_date_and_not_use_checkpoint_and_cursor_exists_uses_begin_date(
    runner, cmd, cli_state, file_event_extractor
):
    begin_date = get_test_date_str(days_ago=1)
    result = runner.invoke(cli, ["security-data", *cmd, "--begin", begin_date], obj=cli_state)

    actual_ts = get_filter_value_from_json(
        file_event_extractor.extract.call_args[0][1], filter_index=0
    )
    expected_ts = "{0}T00:00:00.000Z".format(begin_date)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(file_event_extractor, EventTimestamp._term)


@parametrize_search_output_cmds
def test_when_end_date_is_before_begin_date_causes_exit(runner, cmd, cli_state):
    begin_date = get_test_date_str(days_ago=1)
    end_date = get_test_date_str(days_ago=3)
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", begin_date, "--end", end_date], obj=cli_state
    )
    assert result.exit_code == 2
    assert "'--begin': cannot be after --end date" in result.output


def test_print_with_only_begin_calls_extract_with_expected_args(
    runner, cli_state, file_event_extract_func, stdout_logger, begin_option
):
    result = runner.invoke(cli, ["security-data", "print", "--begin", "1h"], obj=cli_state)
    file_event_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        checkpoint_name=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        saved_search=None,
        output_logger=stdout_logger.return_value,
    )
    assert result.exit_code == 0


def test_send_to_with_only_begin_calls_extract_with_expected_args(
    runner, cli_state, file_event_extract_func, server_logger, begin_option
):
    result = runner.invoke(
        cli, ["security-data", "send-to", "localhost", "--begin", "1h"], obj=cli_state
    )
    file_event_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        checkpoint_name=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        saved_search=None,
        output_logger=server_logger.return_value,
    )
    assert result.exit_code == 0


def test_write_to_with_only_begin_calls_extract_with_expected_args(
    runner, cli_state, file_event_extract_func, file_logger, begin_option
):
    result = runner.invoke(
        cli, ["security-data", "write-to", "test_file", "--begin", "1h"], obj=cli_state
    )
    file_event_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        checkpoint_name=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        saved_search=None,
        output_logger=file_logger.return_value,
    )
    assert result.exit_code == 0


@parametrize_search_output_cmds
def test_with_use_checkpoint_and_without_begin_and_without_checkpoint_causes_expected_error(
    runner, cmd, cli_state, file_event_cursor_without_checkpoint
):
    result = runner.invoke(cli, ["security-data", *cmd, "--use-checkpoint", "test"], obj=cli_state)
    assert result.exit_code == 2
    assert (
        "--begin date is required for --use-checkpoint when no checkpoint exists yet."
        in result.output
    )


@parametrize_search_output_cmds
def test_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    runner,
    cmd,
    cli_state,
    file_event_extract_func,
    begin_option,
    file_event_cursor_without_checkpoint,
    stdout_logger,
    server_logger,
    file_logger,
    mocker,
):
    result = runner.invoke(
        cli, ["security-data", *cmd, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    file_event_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=file_event_cursor_without_checkpoint.return_value,
        checkpoint_name="test",
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        saved_search=None,
        output_logger=mocker.ANY,
    )


@parametrize_search_output_cmds
def test_with_use_checkpoint_and_with_begin_and_with_checkpoint_calls_extract_with_begin_date_none(
    runner,
    cmd,
    cli_state,
    file_event_extract_func,
    file_event_cursor_with_checkpoint,
    stdout_logger,
    server_logger,
    file_logger,
    mocker,
):
    result = runner.invoke(
        cli, ["security-data", *cmd, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    file_event_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=file_event_cursor_with_checkpoint.return_value,
        checkpoint_name="test",
        filter_list=cli_state.search_filters,
        begin=None,
        end=None,
        advanced_query=None,
        saved_search=None,
        output_logger=mocker.ANY,
    )
    assert "checkpoint of 2020-01-20T06:00:00+00:00 exists" in result.output


@parametrize_search_output_cmds
def test_extract_when_given_invalid_exposure_type_causes_exit(runner, cmd, cli_state):
    result = runner.invoke(cli, ["security-data", *cmd, "--begin", "1d", "-t", "NotValid"])
    assert result.exit_code == 2
    assert "invalid choice: NotValid" in result.output


@parametrize_search_output_cmds
def test_when_given_username_uses_username_filter(runner, cmd, cli_state, file_event_extractor):
    c42_username = "test@code42.com"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--c42-username", c42_username], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(DeviceUsername.is_in([c42_username])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_actor_is_uses_username_filter(runner, cmd, cli_state, file_event_extractor):
    actor_name = "test.testerson"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--actor", actor_name], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(Actor.is_in([actor_name])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_md5_uses_md5_filter(runner, cmd, cli_state, file_event_extractor):
    md5 = "abcd12345"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--md5", md5], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(MD5.is_in([md5])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_sha256_uses_sha256_filter(runner, cmd, cli_state, file_event_extractor):
    sha_256 = "abcd12345"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--sha256", sha_256], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(SHA256.is_in([sha_256])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_source_uses_source_filter(runner, cmd, cli_state, file_event_extractor):
    source = "Gmail"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--source", source], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(Source.is_in([source])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_file_name_uses_file_name_filter(runner, cmd, cli_state, file_event_extractor):
    filename = "test.txt"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--file-name", filename], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(FileName.is_in([filename])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_file_path_uses_file_path_filter(runner, cmd, cli_state, file_event_extractor):
    filepath = "C:\\Program Files"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--file-path", filepath], obj=cli_state
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(FilePath.is_in([filepath])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_process_owner_uses_process_owner_filter(
    runner, cmd, cli_state, file_event_extractor
):
    process_owner = "root"
    result = runner.invoke(
        cli,
        ["security-data", *cmd, "--begin", "1h", "--process-owner", process_owner],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(ProcessOwner.is_in([process_owner])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_tab_url_uses_process_tab_url_filter(
    runner, cmd, cli_state, file_event_extractor
):
    tab_url = "https://example.com"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--tab-url", tab_url], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(TabURL.is_in([tab_url])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_exposure_types_uses_exposure_type_is_in_filter(
    runner, cmd, cli_state, file_event_extractor
):
    exposure_type = "SharedViaLink"
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--type", exposure_type], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(ExposureType.is_in([exposure_type])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_include_non_exposure_does_not_include_exposure_type_exists(
    runner, cmd, cli_state, file_event_extractor
):
    result = runner.invoke(
        cli, ["security-data", *cmd, "--begin", "1h", "--include-non-exposure"], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(ExposureType.exists()) not in filter_strings


@parametrize_search_output_cmds
def test_when_not_given_include_non_exposure_includes_exposure_type_exists(
    runner, cmd, cli_state, file_event_extractor
):
    result = runner.invoke(cli, ["security-data", *cmd, "--begin", "1h"], obj=cli_state,)
    filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
    assert str(ExposureType.exists()) in filter_strings


@parametrize_search_output_cmds
def test_when_given_multiple_search_args_uses_expected_filters(
    runner, cmd, cli_state, file_event_extractor
):
    process_owner = "root"
    c42_username = "test@code42.com"
    filename = "test.txt"
    result = runner.invoke(
        cli,
        [
            "security-data",
            *cmd,
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
    assert str(ProcessOwner.is_in([process_owner])) in filter_strings
    assert str(FileName.is_in([filename])) in filter_strings
    assert str(DeviceUsername.is_in([c42_username])) in filter_strings


@parametrize_search_output_cmds
def test_when_given_include_non_exposure_and_exposure_types_causes_exit(
    runner, cmd, cli_state, file_event_extractor
):
    result = runner.invoke(
        cli,
        [
            "security-data",
            *cmd,
            "--begin",
            "1h",
            "--include-non-exposure",
            "--type",
            "SharedViaLink",
        ],
        obj=cli_state,
    )
    assert result.exit_code == 2


@parametrize_search_output_cmds
def test_when_extraction_handles_error_expected_message_logged_and_printed_and_global_errored_flag_set(
    runner, cmd, cli_state, mocker, caplog
):
    errors.ERRORED = False
    exception_msg = "Test Exception"

    def file_search_error(x):
        raise Exception(exception_msg)

    cli_state.sdk.securitydata.search_file_events.side_effect = file_search_error
    with caplog.at_level(logging.ERROR):
        result = runner.invoke(cli, ["security-data", *cmd, "--begin", "1d"], obj=cli_state)
        assert exception_msg in result.output
        assert exception_msg in caplog.text
        assert errors.ERRORED


@parametrize_search_output_cmds
def test_saved_search_calls_extractor_extract_and_saved_search_execute(
    runner, cmd, cli_state, file_event_extractor
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
    result = runner.invoke(cli, ["security-data", *cmd, "--saved-search", "test_id"], obj=cli_state)
    assert file_event_extractor.extract.call_count == 1
    assert str(file_event_extractor.extract.call_args[0][0]) in str(query)
    assert str(file_event_extractor.extract.call_args[0][1]) in str(query)


def test_saved_search_list_calls_get_method(runner, cli_state):
    result = runner.invoke(cli, ["security-data", "saved-search", "list"], obj=cli_state)
    assert cli_state.sdk.securitydata.savedsearches.get.call_count == 1


def test_show_detail_calls_get_by_id_method(runner, cli_state):
    test_id = "test_id"
    result = runner.invoke(cli, ["security-data", "saved-search", "show", test_id], obj=cli_state)
    cli_state.sdk.securitydata.savedsearches.get_by_id.assert_called_once_with(test_id)
