import json
import logging

import py42.sdk.queries.fileevents.filters as f
import pytest
from c42eventextractor.extractors import FileEventExtractor
from py42.sdk.queries.fileevents.file_event_query import FileEventQuery
from py42.sdk.queries.fileevents.filters import RiskIndicator
from py42.sdk.queries.fileevents.filters import RiskSeverity
from py42.sdk.queries.fileevents.filters.file_filter import FileCategory
from tests.cmds.conftest import filter_term_is_in_call_args
from tests.cmds.conftest import get_filter_value_from_json
from tests.cmds.conftest import get_mark_for_search_and_send_to
from tests.conftest import get_test_date_str

from code42cli import errors
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.logger.enums import ServerProtocol
from code42cli.main import cli

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
ADVANCED_QUERY_VALUES = {
    "within_last_value": "P30D",
    "hostname_1": "DESKTOP-H88BEKO",
    "hostname_2": "W10E-X64-FALLCR",
    "event_type": "CREATED",
}
ADVANCED_QUERY_JSON = """
{{
    "purpose": "USER_EXECUTED_SEARCH",
    "groups": [
        {{
            "filterClause": "AND",
            "filters": [
                {{
                    "value": "{within_last_value}",
                    "operator": "WITHIN_THE_LAST",
                    "term": "eventTimestamp"
                }}
            ]
        }},
        {{
            "filterClause": "AND",
            "filters": [
                {{
                    "value": ".*",
                    "operator": "IS",
                    "term": "fileName"
                }}
            ]
        }},
        {{
            "filterClause": "OR",
            "filters": [
                {{
                    "value": "{hostname_1}",
                    "operator": "IS",
                    "term": "osHostName"
                }},
                {{
                    "value": "{hostname_2}",
                    "operator": "IS",
                    "term": "osHostName"
                }}
            ]
        }},
        {{
            "filterClause": "OR",
            "filters": [
                {{
                    "value": "{event_type}",
                    "operator": "IS",
                    "term": "eventType"
                }}
            ]
        }}
    ],
    "pgSize": 100,
    "pgNum": 1
}}""".format(
    **ADVANCED_QUERY_VALUES
)
advanced_query_incompat_test_params = pytest.mark.parametrize(
    "arg",
    [
        ("--begin", "1d"),
        ("--end", "1d"),
        ("--c42-username", "test@example.com"),
        ("--actor", "test.testerson"),
        ("--md5", "abcd1234"),
        ("--sha256", "abcdefg12345678"),
        ("--source", "Gmail"),
        ("--file-name", "test.txt"),
        ("--file-path", "C:\\Program Files"),
        ("--file-category", "IMAGE"),
        ("--process-owner", "root"),
        ("--tab-url", "https://example.com"),
        ("--type", "SharedViaLink"),
        ("--include-non-exposure",),
        ("--risk-indicator", "PUBLIC_CORPORATE_BOX"),
        ("--risk-severity", "LOW"),
    ],
)
saved_search_incompat_test_params = pytest.mark.parametrize(
    "arg",
    [
        ("--begin", "1d"),
        ("--end", "1d"),
        ("--c42-username", "test@example.com"),
        ("--actor", "test.testerson"),
        ("--md5", "abcd1234"),
        ("--sha256", "abcdefg12345678"),
        ("--source", "Gmail"),
        ("--file-name", "test.txt"),
        ("--file-path", "C:\\Program Files"),
        ("--file-category", "IMAGE"),
        ("--process-owner", "root"),
        ("--tab-url", "https://example.com"),
        ("--type", "SharedViaLink"),
        ("--include-non-exposure",),
        ("--use-checkpoint", "test"),
        ("--risk-indicator", "PUBLIC_CORPORATE_BOX"),
        ("--risk-severity", "LOW"),
    ],
)
search_and_send_to_test = get_mark_for_search_and_send_to("security-data")


@pytest.fixture
def file_event_cursor_with_checkpoint(mocker):
    mock = mocker.patch("code42cli.cmds.securitydata._get_file_event_cursor_store")
    mock_cursor = mocker.MagicMock(spec=FileEventCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    mock.expected_timestamp = "2020-01-20T06:00:00+00:00"
    return mock


@pytest.fixture
def file_event_cursor_without_checkpoint(mocker):
    mock = mocker.patch("code42cli.cmds.securitydata._get_file_event_cursor_store")
    mock_cursor = mocker.MagicMock(spec=FileEventCursorStore)
    mock_cursor.get.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch("code42cli.cmds.securitydata.convert_datetime_to_timestamp")
    mock.return_value = BEGIN_TIMESTAMP
    mock.expected_timestamp = "2020-01-01T06:00:00.000Z"
    return mock


@pytest.fixture
def send_to_logger_factory(mocker):
    return mocker.patch("code42cli.cmds.search._try_get_logger_for_server")


# @search_and_send_to_test
# def test_search_and_send_to_when_advanced_query_passed_as_json_string_builds_expected_query(
#     runner, cli_state, command
# ):
#     runner.invoke(
#         cli, [*command, "--advanced-query", ADVANCED_QUERY_JSON], obj=cli_state
#     )
#     query = cli_state.sdk.securitydata.search_all_file_events.call_args.args[0]
#     passed_filter_groups = query._filter_group_list
#     expected_event_filter = f.EventTimestamp.within_the_last(
#         ADVANCED_QUERY_VALUES["within_last_value"]
#     )
#     expected_hostname_filter = f.OSHostname.is_in(
#         [ADVANCED_QUERY_VALUES["hostname_1"], ADVANCED_QUERY_VALUES["hostname_2"]]
#     )
#     expected_event_type_filter = f.EventType.is_in(
#         [ADVANCED_QUERY_VALUES["event_type"]]
#     )
#     expected_event_type_filter.filter_clause = "OR"
#     assert expected_event_filter in passed_filter_groups
#     assert expected_hostname_filter in passed_filter_groups
#     assert expected_event_type_filter in passed_filter_groups


@search_and_send_to_test
def test_search_and_send_to_when_advanced_query_passed_as_filename_builds_expected_query(
    runner, cli_state, command
):
    with runner.isolated_filesystem():
        with open("query.json", "w") as jsonfile:
            jsonfile.write(ADVANCED_QUERY_JSON)

        runner.invoke(cli, [*command, "--advanced-query", "@query.json"], obj=cli_state)
        query = cli_state.sdk.securitydata.search_all_file_events.call_args.args[0]
        passed_filter_groups = query._filter_group_list
        expected_event_filter = f.EventTimestamp.within_the_last(
            ADVANCED_QUERY_VALUES["within_last_value"]
        )
        expected_hostname_filter = f.OSHostname.is_in(
            [ADVANCED_QUERY_VALUES["hostname_1"], ADVANCED_QUERY_VALUES["hostname_2"]]
        )
        expected_event_type_filter = f.EventType.is_in(
            [ADVANCED_QUERY_VALUES["event_type"]]
        )
        expected_event_type_filter.filter_clause = "OR"
        assert expected_event_filter in passed_filter_groups
        assert expected_hostname_filter in passed_filter_groups
        assert expected_event_type_filter in passed_filter_groups


# @search_and_send_to_test
# def test_search_and_send_to_when_advanced_query_passed_non_existent_filename_raises_error(
#     runner, cli_state, command
# ):
#     with runner.isolated_filesystem():
#         result = runner.invoke(
#             cli, [*command, "--advanced-query", "@not_a_file"], obj=cli_state
#         )
#         assert result.exit_code == 2
#         assert "Could not open file: not_a_file" in result.stdout
# 
# 
# @advanced_query_incompat_test_params
# def test_search_with_advanced_query_and_incompatible_argument_errors(
#     runner, arg, cli_state
# ):
#     result = runner.invoke(
#         cli,
#         ["security-data", "search", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
#         obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert f"{arg[0]} can't be used with: --advanced-query" in result.output
# 
# 
# @advanced_query_incompat_test_params
# def test_send_to_with_advanced_query_and_incompatible_argument_errors(
#     runner, arg, cli_state
# ):
#     result = runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--advanced-query",
#             ADVANCED_QUERY_JSON,
#             *arg,
#         ],
#         obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert f"{arg[0]} can't be used with: --advanced-query" in result.output
# 
# 
# @saved_search_incompat_test_params
# def test_search_with_saved_search_and_incompatible_argument_errors(
#     runner, arg, cli_state
# ):
#     result = runner.invoke(
#         cli,
#         ["security-data", "search", "--saved-search", "test_id", *arg],
#         obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert f"{arg[0]} can't be used with: --saved-search" in result.output
# 
# 
# @saved_search_incompat_test_params
# def test_send_to_with_saved_search_and_incompatible_argument_errors(
#     runner, arg, cli_state
# ):
#     result = runner.invoke(
#         cli,
#         ["security-data", "send-to", "0.0.0.0", "--saved-search", "test_id", *arg],
#         obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert f"{arg[0]} can't be used with: --saved-search" in result.output
# 
# 
# @pytest.mark.parametrize("protocol", (ServerProtocol.UDP, ServerProtocol.TCP))
# def test_send_to_when_given_ignore_cert_validation_with_non_tls_protocol_fails_expectedly(
#     cli_state, runner, protocol
# ):
#     res = runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--begin",
#             "1d",
#             "--protocol",
#             protocol,
#             "--ignore-cert-validation",
#         ],
#         obj=cli_state,
#     )
#     assert (
#         "'--ignore-cert-validation' can only be used with '--protocol TLS-TCP'"
#         in res.output
#     )
# 
# 
# @pytest.mark.parametrize("protocol", (ServerProtocol.UDP, ServerProtocol.TCP))
# def test_send_to_when_given_certs_with_non_tls_protocol_fails_expectedly(
#     cli_state, runner, protocol
# ):
#     res = runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--begin",
#             "1d",
#             "--protocol",
#             protocol,
#             "--certs",
#             "certs.pem",
#         ],
#         obj=cli_state,
#     )
#     assert "'--certs' can only be used with '--protocol TLS-TCP'" in res.output
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_begin_and_end_dates_uses_expected_query(
#     runner, cli_state, file_event_extractor, command
# ):
#     begin_date = get_test_date_str(days_ago=89)
#     end_date = get_test_date_str(days_ago=1)
#     runner.invoke(
#         cli,
#         [
#             *command,
#             "--begin",
#             get_test_date_str(days_ago=89),
#             "--end",
#             get_test_date_str(days_ago=1),
#         ],
#         obj=cli_state,
#     )
#     filters = file_event_extractor.extract.call_args[0][1]
#     actual_begin = get_filter_value_from_json(filters, filter_index=0)
#     expected_begin = f"{begin_date}T00:00:00.000Z"
#     actual_end = get_filter_value_from_json(filters, filter_index=1)
#     expected_end = f"{end_date}T23:59:59.999Z"
#     assert actual_begin == expected_begin
#     assert actual_end == expected_end
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_begin_and_end_date_and_time_uses_expected_query(
#     runner, cli_state, file_event_extractor, command
# ):
#     begin_date = get_test_date_str(days_ago=89)
#     end_date = get_test_date_str(days_ago=1)
#     time = "15:33:02"
#     runner.invoke(
#         cli,
#         [*command, "--begin", f"{begin_date} {time}", "--end", f"{end_date} {time}"],
#         obj=cli_state,
#     )
#     filters = file_event_extractor.extract.call_args[0][1]
#     actual_begin = get_filter_value_from_json(filters, filter_index=0)
#     expected_begin = f"{begin_date}T{time}.000Z"
#     actual_end = get_filter_value_from_json(filters, filter_index=1)
#     expected_end = f"{end_date}T{time}.000Z"
#     assert actual_begin == expected_begin
#     assert actual_end == expected_end
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_begin_date_and_time_without_seconds_uses_expected_query(
#     runner, cli_state, file_event_extractor, command
# ):
#     date = get_test_date_str(days_ago=89)
#     time = "15:33"
#     runner.invoke(
#         cli, [*command, "--begin", f"{date} {time}"], obj=cli_state,
#     )
#     actual = get_filter_value_from_json(
#         file_event_extractor.extract.call_args[0][1], filter_index=0
#     )
#     expected = f"{date}T{time}:00.000Z"
#     assert actual == expected
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_end_date_and_time_uses_expected_query(
#     runner, cli_state, file_event_extractor, command
# ):
#     begin_date = get_test_date_str(days_ago=10)
#     end_date = get_test_date_str(days_ago=1)
#     time = "15:33"
#     runner.invoke(
#         cli,
#         [*command, "--begin", begin_date, "--end", f"{end_date} {time}"],
#         obj=cli_state,
#     )
#     actual = get_filter_value_from_json(
#         file_event_extractor.extract.call_args[0][1], filter_index=1
#     )
#     expected = f"{end_date}T{time}:00.000Z"
#     assert actual == expected
# 
# 
# @search_and_send_to_test
# def test_search_send_to_when_given_begin_date_more_than_ninety_days_back_errors(
#     runner, cli_state, command
# ):
#     result = runner.invoke(
#         cli,
#         [*command, "--begin", get_test_date_str(days_ago=91) + " 12:51:00"],
#         obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert "must be within 90 days" in result.output
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_begin_date_past_90_days_and_use_checkpoint_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
#     runner, cli_state, file_event_cursor_with_checkpoint, file_event_extractor, command
# ):
#     begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
#     runner.invoke(
#         cli,
#         [*command, "--begin", begin_date, "--use-checkpoint", "test"],
#         obj=cli_state,
#     )
#     assert not filter_term_is_in_call_args(
#         file_event_extractor, f.InsertionTimestamp._term
#     )
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_begin_date_and_not_use_checkpoint_and_cursor_exists_uses_begin_date(
#     runner, cli_state, file_event_extractor, command
# ):
#     begin_date = get_test_date_str(days_ago=1)
#     runner.invoke(cli, [*command, "--begin", begin_date], obj=cli_state)
#     actual_ts = get_filter_value_from_json(
#         file_event_extractor.extract.call_args[0][1], filter_index=0
#     )
#     expected_ts = f"{begin_date}T00:00:00.000Z"
#     assert actual_ts == expected_ts
#     assert filter_term_is_in_call_args(file_event_extractor, f.EventTimestamp._term)
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_end_date_is_before_begin_date_causes_exit(
#     runner, cli_state, command
# ):
#     begin_date = get_test_date_str(days_ago=1)
#     end_date = get_test_date_str(days_ago=3)
#     result = runner.invoke(
#         cli, [*command, "--begin", begin_date, "--end", end_date], obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert "'--begin': cannot be after --end date" in result.output
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_with_only_begin_calls_extract_with_expected_args(
#     runner, cli_state, file_event_extractor, begin_option, command
# ):
#     result = runner.invoke(cli, [*command, "--begin", "1h"], obj=cli_state)
#     assert result.exit_code == 0
#     assert (
#         str(file_event_extractor.extract.call_args[0][1])
#         == f'{{"filterClause":"AND", "filters":[{{"operator":"ON_OR_AFTER", "term":"eventTimestamp", '
#         f'"value":"{begin_option.expected_timestamp}"}}]}}'
#     )
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_with_use_checkpoint_and_without_begin_and_without_checkpoint_causes_expected_error(
#     runner, cli_state, file_event_cursor_without_checkpoint, command
# ):
#     result = runner.invoke(cli, [*command, "--use-checkpoint", "test"], obj=cli_state)
#     assert result.exit_code == 2
#     assert (
#         "--begin date is required for --use-checkpoint when no checkpoint exists yet."
#         in result.output
#     )
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
#     runner,
#     cli_state,
#     file_event_extractor,
#     begin_option,
#     file_event_cursor_without_checkpoint,
#     command,
# ):
#     result = runner.invoke(
#         cli, [*command, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state,
#     )
#     assert result.exit_code == 0
#     assert len(file_event_extractor.extract.call_args[0]) == 2
#     assert begin_option.expected_timestamp in str(
#         file_event_extractor.extract.call_args[0][1]
#     )
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_with_use_checkpoint_and_with_begin_and_with_stored_checkpoint_calls_extract_with_checkpoint_and_ignores_begin_arg(
#     runner, cli_state, file_event_extractor, file_event_cursor_with_checkpoint, command,
# ):
#     result = runner.invoke(
#         cli, [*command, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state,
#     )
#     assert result.exit_code == 0
#     assert len(file_event_extractor.extract.call_args[0]) == 1
#     assert (
#         f"checkpoint of {file_event_cursor_with_checkpoint.expected_timestamp} exists"
#         in result.output
#     )
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_invalid_exposure_type_causes_exit(
#     runner, cli_state, command
# ):
#     result = runner.invoke(
#         cli, [*command, "--begin", "1d", "-t", "NotValid"], obj=cli_state,
#     )
#     assert result.exit_code == 2
#     assert "invalid choice: NotValid" in result.output
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_username_uses_username_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     c42_username = "test@example.com"
#     command = [*command, "--begin", "1h", "--c42-username", c42_username]
#     runner.invoke(
#         cli, [*command], obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.DeviceUsername.is_in([c42_username])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_actor_is_uses_username_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     actor_name = "test.testerson"
#     command = [*command, "--begin", "1h", "--actor", actor_name]
#     runner.invoke(
#         cli, [*command], obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.Actor.is_in([actor_name])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_md5_uses_md5_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     md5 = "abcd12345"
#     command = [*command, "--begin", "1h", "--md5", md5]
#     runner.invoke(cli, [*command], obj=cli_state)
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.MD5.is_in([md5])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_sha256_uses_sha256_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     sha_256 = "abcd12345"
#     command = [*command, "--begin", "1h", "--sha256", sha_256]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.SHA256.is_in([sha_256])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_source_uses_source_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     source = "Gmail"
#     command = [*command, "--begin", "1h", "--source", source]
#     runner.invoke(cli, command, obj=cli_state)
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.Source.is_in([source])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_file_name_uses_file_name_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     filename = "test.txt"
#     command = [*command, "--begin", "1h", "--file-name", filename]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.FileName.is_in([filename])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_file_path_uses_file_path_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     filepath = "C:\\Program Files"
#     command = [*command, "--begin", "1h", "--file-path", filepath]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.FilePath.is_in([filepath])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_file_category_uses_file_category_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     file_category = FileCategory.IMAGE
#     command = [*command, "--begin", "1h", "--file-category", file_category]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.FileCategory.is_in([file_category])) in filter_strings
# 
# 
# @pytest.mark.parametrize(
#     "category_choice",
#     [
#         ("AUDIO", FileCategory.AUDIO),
#         ("DOCUMENT", FileCategory.DOCUMENT),
#         ("EXECUTABLE", FileCategory.EXECUTABLE),
#         ("IMAGE", FileCategory.IMAGE),
#         ("PDF", FileCategory.PDF),
#         ("PRESENTATION", FileCategory.PRESENTATION),
#         ("SCRIPT", FileCategory.SCRIPT),
#         ("SOURCE_CODE", FileCategory.SOURCE_CODE),
#         ("SPREADSHEET", FileCategory.SPREADSHEET),
#         ("VIDEO", FileCategory.VIDEO),
#         ("VIRTUAL_DISK_IMAGE", FileCategory.VIRTUAL_DISK_IMAGE),
#         ("ARCHIVE", FileCategory.ZIP),
#         ("ZIP", FileCategory.ZIP),
#         ("Zip", FileCategory.ZIP),
#     ],
# )
# def test_all_caps_file_category_choices_convert_to_filecategory_constant(
#     runner, cli_state, file_event_extractor, category_choice
# ):
#     ALL_CAPS_VALUE, camelCaseValue = category_choice
#     command = [
#         "security-data",
#         "search",
#         "--begin",
#         "1h",
#         "--file-category",
#         ALL_CAPS_VALUE,
#     ]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.FileCategory.is_in([camelCaseValue])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_process_owner_uses_process_owner_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     process_owner = "root"
#     command = [*command, "-b", "1h", "--process-owner", process_owner]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.ProcessOwner.is_in([process_owner])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_tab_url_uses_process_tab_url_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     tab_url = "https://example.com"
#     command = [*command, "--begin", "1h", "--tab-url", tab_url]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.TabURL.is_in([tab_url])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_exposure_types_uses_exposure_type_is_in_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     exposure_type = "SharedViaLink"
#     command = [*command, "--begin", "1h", "--type", exposure_type]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.ExposureType.is_in([exposure_type])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_include_non_exposure_does_not_include_exposure_type_exists(
#     runner, cli_state, file_event_extractor, command
# ):
#     runner.invoke(
#         cli, [*command, "--begin", "1h", "--include-non-exposure"], obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.ExposureType.exists()) not in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_not_given_include_non_exposure_includes_exposure_type_exists(
#     runner, cli_state, file_event_extractor, command
# ):
#     runner.invoke(
#         cli, [*command, "--begin", "1h"], obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.ExposureType.exists()) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_multiple_search_args_uses_expected_filters(
#     runner, cli_state, file_event_extractor, command
# ):
#     process_owner = "root"
#     c42_username = "test@example.com"
#     filename = "test.txt"
#     runner.invoke(
#         cli,
#         [
#             *command,
#             "--begin",
#             "1h",
#             "--process-owner",
#             process_owner,
#             "--c42-username",
#             c42_username,
#             "--file-name",
#             filename,
#         ],
#         obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.ProcessOwner.is_in([process_owner])) in filter_strings
#     assert str(f.FileName.is_in([filename])) in filter_strings
#     assert str(f.DeviceUsername.is_in([c42_username])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_include_non_exposure_and_exposure_types_causes_exit(
#     runner, cli_state, file_event_extractor, command
# ):
#     result = runner.invoke(
#         cli,
#         [
#             *command,
#             "--begin",
#             "1h",
#             "--include-non-exposure",
#             "--type",
#             "SharedViaLink",
#         ],
#         obj=cli_state,
#     )
#     assert result.exit_code == 2
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_risk_indicator_uses_risk_indicator_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     risk_indicator = RiskIndicator.MessagingServiceUploads.SLACK
#     command = [*command, "--begin", "1h", "--risk-indicator", risk_indicator]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.RiskIndicator.is_in([risk_indicator])) in filter_strings
# 
# 
# @pytest.mark.parametrize(
#     "indicator_choice",
#     [
#         ("PUBLIC_CORPORATE_BOX", RiskIndicator.CloudDataExposures.PUBLIC_CORPORATE_BOX),
#         (
#             "PUBLIC_CORPORATE_GOOGLE",
#             RiskIndicator.CloudDataExposures.PUBLIC_CORPORATE_GOOGLE_DRIVE,
#         ),
#         (
#             "PUBLIC_CORPORATE_ONEDRIVE",
#             RiskIndicator.CloudDataExposures.PUBLIC_CORPORATE_ONEDRIVE,
#         ),
#         ("SENT_CORPORATE_GMAIL", RiskIndicator.CloudDataExposures.SENT_CORPORATE_GMAIL),
#         ("SHARED_CORPORATE_BOX", RiskIndicator.CloudDataExposures.SHARED_CORPORATE_BOX),
#         (
#             "SHARED_CORPORATE_GOOGLE_DRIVE",
#             RiskIndicator.CloudDataExposures.SHARED_CORPORATE_GOOGLE_DRIVE,
#         ),
#         (
#             "SHARED_CORPORATE_ONEDRIVE",
#             RiskIndicator.CloudDataExposures.SHARED_CORPORATE_ONEDRIVE,
#         ),
#         ("AMAZON_DRIVE", RiskIndicator.CloudStorageUploads.AMAZON_DRIVE),
#         ("BOX", RiskIndicator.CloudStorageUploads.BOX),
#         ("DROPBOX", RiskIndicator.CloudStorageUploads.DROPBOX),
#         ("GOOGLE_DRIVE", RiskIndicator.CloudStorageUploads.GOOGLE_DRIVE),
#         ("ICLOUD", RiskIndicator.CloudStorageUploads.ICLOUD),
#         ("MEGA", RiskIndicator.CloudStorageUploads.MEGA),
#         ("ONEDRIVE", RiskIndicator.CloudStorageUploads.ONEDRIVE),
#         ("ZOHO", RiskIndicator.CloudStorageUploads.ZOHO),
#         ("BITBUCKET", RiskIndicator.CodeRepositoryUploads.BITBUCKET),
#         ("GITHUB", RiskIndicator.CodeRepositoryUploads.GITHUB),
#         ("GITLAB", RiskIndicator.CodeRepositoryUploads.GITLAB),
#         ("SOURCEFORGE", RiskIndicator.CodeRepositoryUploads.SOURCEFORGE),
#         ("STASH", RiskIndicator.CodeRepositoryUploads.STASH),
#         ("163.COM", RiskIndicator.EmailServiceUploads.ONESIXTHREE_DOT_COM),
#         ("126.COM", RiskIndicator.EmailServiceUploads.ONETWOSIX_DOT_COM),
#         ("AOL", RiskIndicator.EmailServiceUploads.AOL),
#         ("COMCAST", RiskIndicator.EmailServiceUploads.COMCAST),
#         ("GMAIL", RiskIndicator.EmailServiceUploads.GMAIL),
#         ("ICLOUD_MAIL", RiskIndicator.EmailServiceUploads.ICLOUD),
#         ("MAIL.COM", RiskIndicator.EmailServiceUploads.MAIL_DOT_COM),
#         ("OUTLOOK", RiskIndicator.EmailServiceUploads.OUTLOOK),
#         ("PROTONMAIL", RiskIndicator.EmailServiceUploads.PROTONMAIL),
#         ("QQMAIL", RiskIndicator.EmailServiceUploads.QQMAIL),
#         ("SINA_MAIL", RiskIndicator.EmailServiceUploads.SINA_MAIL),
#         ("SOHU_MAIL", RiskIndicator.EmailServiceUploads.SOHU_MAIL),
#         ("YAHOO", RiskIndicator.EmailServiceUploads.YAHOO),
#         ("ZOHO_MAIL", RiskIndicator.EmailServiceUploads.ZOHO_MAIL),
#         ("AIRDROP", RiskIndicator.ExternalDevices.AIRDROP),
#         ("REMOVABLE_MEDIA", RiskIndicator.ExternalDevices.REMOVABLE_MEDIA),
#         ("AUDIO", RiskIndicator.FileCategories.AUDIO),
#         ("DOCUMENT", RiskIndicator.FileCategories.DOCUMENT),
#         ("EXECUTABLE", RiskIndicator.FileCategories.EXECUTABLE),
#         ("IMAGE", RiskIndicator.FileCategories.IMAGE),
#         ("PDF", RiskIndicator.FileCategories.PDF),
#         ("PRESENTATION", RiskIndicator.FileCategories.PRESENTATION),
#         ("SCRIPT", RiskIndicator.FileCategories.SCRIPT),
#         ("SOURCE_CODE", RiskIndicator.FileCategories.SOURCE_CODE),
#         ("SPREADSHEET", RiskIndicator.FileCategories.SPREADSHEET),
#         ("VIDEO", RiskIndicator.FileCategories.VIDEO),
#         ("VIRTUAL_DISK_IMAGE", RiskIndicator.FileCategories.VIRTUAL_DISK_IMAGE),
#         ("ZIP", RiskIndicator.FileCategories.ZIP),
#         (
#             "FACEBOOK_MESSENGER",
#             RiskIndicator.MessagingServiceUploads.FACEBOOK_MESSENGER,
#         ),
#         ("MICROSOFT_TEAMS", RiskIndicator.MessagingServiceUploads.MICROSOFT_TEAMS),
#         ("SLACK", RiskIndicator.MessagingServiceUploads.SLACK),
#         ("WHATSAPP", RiskIndicator.MessagingServiceUploads.WHATSAPP),
#         ("OTHER", RiskIndicator.Other.OTHER),
#         ("UNKNOWN", RiskIndicator.Other.UNKNOWN),
#         ("FACEBOOK", RiskIndicator.SocialMediaUploads.FACEBOOK),
#         ("LINKEDIN", RiskIndicator.SocialMediaUploads.LINKEDIN),
#         ("REDDIT", RiskIndicator.SocialMediaUploads.REDDIT),
#         ("TWITTER", RiskIndicator.SocialMediaUploads.TWITTER),
#         ("FILE_MISMATCH", RiskIndicator.UserBehavior.FILE_MISMATCH),
#         ("OFF_HOURS", RiskIndicator.UserBehavior.OFF_HOURS),
#         ("REMOTE", RiskIndicator.UserBehavior.REMOTE),
#         ("FIRST_DESTINATION_USE", RiskIndicator.UserBehavior.FIRST_DESTINATION_USE),
#         ("RARE_DESTINATION_USE", RiskIndicator.UserBehavior.RARE_DESTINATION_USE),
#     ],
# )
# def test_all_caps_risk_indicator_choices_convert_to_risk_indicator_string(
#     runner, cli_state, file_event_extractor, indicator_choice
# ):
#     ALL_CAPS_VALUE, string_value = indicator_choice
#     command = [
#         "security-data",
#         "search",
#         "--begin",
#         "1h",
#         "--risk-indicator",
#         ALL_CAPS_VALUE,
#     ]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.RiskIndicator.is_in([string_value])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_given_risk_severity_uses_risk_severity_filter(
#     runner, cli_state, file_event_extractor, command
# ):
#     risk_severity = RiskSeverity.LOW
#     command = [*command, "--begin", "1h", "--risk-severity", risk_severity]
#     runner.invoke(
#         cli, command, obj=cli_state,
#     )
#     filter_strings = [str(arg) for arg in file_event_extractor.extract.call_args[0]]
#     assert str(f.RiskSeverity.is_in([risk_severity])) in filter_strings
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_when_extraction_handles_error_expected_message_logged_and_printed_and_global_errored_flag_set(
#     runner, cli_state, caplog, command
# ):
#     errors.ERRORED = False
#     exception_msg = "Test Exception"
#     cli_state.sdk.securitydata.search_file_events.side_effect = Exception(exception_msg)
#     with caplog.at_level(logging.ERROR):
#         result = runner.invoke(cli, [*command, "--begin", "1d"], obj=cli_state)
#         assert "Error:" in result.output
#         assert exception_msg in result.output
#         assert exception_msg in caplog.text
#         assert errors.ERRORED
# 
# 
# @search_and_send_to_test
# def test_search_and_send_to_with_or_query_flag_produces_expected_query(
#     runner, cli_state, command
# ):
#     begin_date = get_test_date_str(days_ago=10)
#     test_username = "test@example.com"
#     test_filename = "test.txt"
#     runner.invoke(
#         cli,
#         [
#             *command,
#             "--or-query",
#             "--begin",
#             begin_date,
#             "--c42-username",
#             test_username,
#             "--file-name",
#             test_filename,
#         ],
#         obj=cli_state,
#     )
#     expected_query = {
#         "groupClause": "AND",
#         "groups": [
#             {
#                 "filterClause": "AND",
#                 "filters": [
#                     {"operator": "EXISTS", "term": "exposure", "value": None},
#                     {
#                         "operator": "ON_OR_AFTER",
#                         "term": "eventTimestamp",
#                         "value": f"{begin_date}T00:00:00.000Z",
#                     },
#                 ],
#             },
#             {
#                 "filterClause": "OR",
#                 "filters": [
#                     {
#                         "operator": "IS",
#                         "term": "deviceUserName",
#                         "value": "test@example.com",
#                     },
#                     {"operator": "IS", "term": "fileName", "value": "test.txt"},
#                 ],
#             },
#         ],
#         "pgNum": 1,
#         "pgSize": 10000,
#         "srtDir": "asc",
#         "srtKey": "insertionTimestamp",
#     }
#     actual_query = json.loads(
#         str(cli_state.sdk.securitydata.search_file_events.call_args[0][0])
#     )
#     assert actual_query == expected_query
# 
# 
# def test_saved_search_calls_extractor_extract_and_saved_search_execute(
#     runner, cli_state, file_event_extractor
# ):
#     search_query = {
#         "groupClause": "AND",
#         "groups": [
#             {
#                 "filterClause": "AND",
#                 "filters": [
#                     {
#                         "operator": "ON_OR_AFTER",
#                         "term": "eventTimestamp",
#                         "value": "2020-05-01T00:00:00.000Z",
#                     }
#                 ],
#             },
#             {
#                 "filterClause": "OR",
#                 "filters": [
#                     {"operator": "IS", "term": "eventType", "value": "DELETED"},
#                     {"operator": "IS", "term": "eventType", "value": "EMAILED"},
#                     {"operator": "IS", "term": "eventType", "value": "MODIFIED"},
#                     {"operator": "IS", "term": "eventType", "value": "READ_BY_AP"},
#                     {"operator": "IS", "term": "eventType", "value": "CREATED"},
#                 ],
#             },
#         ],
#         "pgNum": 1,
#         "pgSize": 10000,
#         "srtDir": "asc",
#         "srtKey": "eventId",
#     }
#     query = FileEventQuery.from_dict(search_query)
#     cli_state.sdk.securitydata.savedsearches.get_query.return_value = query
#     runner.invoke(
#         cli, ["security-data", "search", "--saved-search", "test_id"], obj=cli_state
#     )
#     assert file_event_extractor.extract.call_count == 1
#     assert str(file_event_extractor.extract.call_args[0][0]) in str(query)
#     assert str(file_event_extractor.extract.call_args[0][1]) in str(query)
# 
# 
# @pytest.mark.parametrize(
#     "protocol", (ServerProtocol.TLS_TCP, ServerProtocol.TLS_TCP, ServerProtocol.UDP)
# )
# def test_send_to_allows_protocol_arg(cli_state, runner, protocol):
#     res = runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--begin",
#             "1d",
#             "--protocol",
#             protocol,
#         ],
#         obj=cli_state,
#     )
#     assert res.exit_code == 0
# 
# 
# def test_send_to_fails_when_given_unknown_protocol(cli_state, runner):
#     res = runner.invoke(
#         cli,
#         ["security-data", "send-to", "0.0.0.0", "--begin", "1d", "--protocol", "ATM"],
#         obj=cli_state,
#     )
#     assert res.exit_code
# 
# 
# def test_send_to_certs_and_ignore_cert_validation_args_are_incompatible(
#     cli_state, runner
# ):
#     res = runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--begin",
#             "1d",
#             "--protocol",
#             "TLS-TCP",
#             "--certs",
#             "certs/file",
#             "--ignore-cert-validation",
#         ],
#         obj=cli_state,
#     )
#     assert "Error: --ignore-cert-validation can't be used with: --certs" in res.output
# 
# 
# def test_send_to_creates_expected_logger(cli_state, runner, send_to_logger_factory):
#     runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--begin",
#             "1d",
#             "--protocol",
#             "TLS-TCP",
#             "--certs",
#             "certs/file",
#         ],
#         obj=cli_state,
#     )
#     send_to_logger_factory.assert_called_once_with(
#         "0.0.0.0", "TLS-TCP", "RAW-JSON", "certs/file"
#     )
# 
# 
# def test_send_to_when_given_ignore_cert_validation_uses_certs_equal_to_ignore_str(
#     cli_state, runner, send_to_logger_factory
# ):
#     runner.invoke(
#         cli,
#         [
#             "security-data",
#             "send-to",
#             "0.0.0.0",
#             "--begin",
#             "1d",
#             "--protocol",
#             "TLS-TCP",
#             "--ignore-cert-validation",
#         ],
#         obj=cli_state,
#     )
#     send_to_logger_factory.assert_called_once_with(
#         "0.0.0.0", "TLS-TCP", "RAW-JSON", "ignore"
#     )
# 
# 
# def test_saved_search_list_calls_get_method(runner, cli_state):
#     runner.invoke(cli, ["security-data", "saved-search", "list"], obj=cli_state)
#     assert cli_state.sdk.securitydata.savedsearches.get.call_count == 1
# 
# 
# def test_saved_search_show_detail_calls_get_by_id_method(runner, cli_state):
#     test_id = "test_id"
#     runner.invoke(
#         cli, ["security-data", "saved-search", "show", test_id], obj=cli_state
#     )
#     cli_state.sdk.securitydata.savedsearches.get_by_id.assert_called_once_with(test_id)
# 
# 
# def test_saved_search_list_with_format_option_returns_csv_formatted_response(
#     runner, cli_state
# ):
#     cli_state.sdk.securitydata.savedsearches.get.return_value = TEST_LIST_RESPONSE
#     result = runner.invoke(
#         cli, ["security-data", "saved-search", "list", "-f", "CSV"], obj=cli_state
#     )
#     assert "id" in result.output
#     assert "name" in result.output
#     assert "notes" in result.output
# 
#     assert "083f08d-8f33-4cbd-81c4-8d1820b61185" in result.output
#     assert "test-events" in result.output
#     assert "py42 is here" in result.output
# 
# 
# def test_saved_search_list_with_format_option_does_not_return_when_response_is_empty(
#     runner, cli_state
# ):
#     cli_state.sdk.securitydata.savedsearches.get.return_value = TEST_EMPTY_LIST_RESPONSE
#     result = runner.invoke(
#         cli, ["security-data", "saved-search", "list", "-f", "csv"], obj=cli_state
#     )
#     assert "Name,Id" not in result.output
