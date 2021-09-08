import json
import logging

import py42.sdk.queries.alerts.filters as f
import pytest
from py42.exceptions import Py42NotFoundError
from py42.sdk.queries.alerts.alert_query import AlertQuery
from py42.sdk.queries.alerts.filters import AlertState
from tests.cmds.conftest import filter_term_is_in_call_args
from tests.cmds.conftest import get_mark_for_search_and_send_to
from tests.conftest import create_mock_response
from tests.conftest import get_test_date_str

from code42cli import PRODUCT_NAME
from code42cli.cmds import alerts
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.logger.enums import ServerProtocol
from code42cli.main import cli


BEGIN_TIMESTAMP = 1577858400.0
END_TIMESTAMP = 1580450400.0
CURSOR_TIMESTAMP = 1579500000.0
ALERT_SUMMARY_LIST = [{"id": i} for i in range(20)]
ALERT_DETAIL_RESULT = [
    {
        "alerts": [
            {"id": 1, "createdAt": "2020-01-17"},
            {"id": 11, "createdAt": "2020-01-18"},
        ]
    },
    {
        "alerts": [
            {"id": 2, "createdAt": "2020-01-19"},
            {"id": 12, "createdAt": "2020-01-20"},
        ]
    },
    {
        "alerts": [
            {"id": 3, "createdAt": "2020-01-01"},
            {"id": 13, "createdAt": "2020-01-02"},
        ]
    },
    {
        "alerts": [
            {"id": 4, "createdAt": "2020-01-03"},
            {"id": 14, "createdAt": "2020-01-04"},
        ]
    },
    {
        "alerts": [
            {"id": 5, "createdAt": "2020-01-05"},
            {"id": 15, "createdAt": "2020-01-06"},
        ]
    },
    {
        "alerts": [
            {"id": 6, "createdAt": "2020-01-07"},
            {"id": 16, "createdAt": "2020-01-08"},
        ]
    },
    {
        "alerts": [
            {"id": 7, "createdAt": "2020-01-09"},
            {"id": 17, "createdAt": "2020-01-10"},
        ]
    },
    {
        "alerts": [
            {"id": 8, "createdAt": "2020-01-11"},
            {"id": 18, "createdAt": "2020-01-12"},
        ]
    },
    {
        "alerts": [
            {"id": 9, "createdAt": "2020-01-13"},
            {"id": 19, "createdAt": "2020-01-14"},
        ]
    },
    {
        "alerts": [
            {"id": 10, "createdAt": "2020-01-15"},
            {"id": 20, "createdAt": "2020-01-16"},
        ]
    },
]
SORTED_ALERT_DETAILS = [
    {"id": 12, "createdAt": "2020-01-20"},
    {"id": 2, "createdAt": "2020-01-19"},
    {"id": 11, "createdAt": "2020-01-18"},
    {"id": 1, "createdAt": "2020-01-17"},
    {"id": 20, "createdAt": "2020-01-16"},
    {"id": 10, "createdAt": "2020-01-15"},
    {"id": 19, "createdAt": "2020-01-14"},
    {"id": 9, "createdAt": "2020-01-13"},
    {"id": 18, "createdAt": "2020-01-12"},
    {"id": 8, "createdAt": "2020-01-11"},
    {"id": 17, "createdAt": "2020-01-10"},
    {"id": 7, "createdAt": "2020-01-09"},
    {"id": 16, "createdAt": "2020-01-08"},
    {"id": 6, "createdAt": "2020-01-07"},
    {"id": 15, "createdAt": "2020-01-06"},
    {"id": 5, "createdAt": "2020-01-05"},
    {"id": 14, "createdAt": "2020-01-04"},
    {"id": 4, "createdAt": "2020-01-03"},
    {"id": 13, "createdAt": "2020-01-02"},
    {"id": 3, "createdAt": "2020-01-01"},
]
ADVANCED_QUERY_VALUES = {
    "state_1": "OPEN",
    "state_2": "PENDING",
    "state_3": "IN_PROGRESS",
    "actor": "test@example.com",
    "on_or_after": "2020-01-01T06:00:00.000000Z",
    "on_or_after_timestamp": 1577858400.0,
    "on_or_before": "2020-02-01T06:00:00.000000Z",
    "on_or_before_timestamp": 1580536800.0,
    "rule_id": "xyz123",
}
ADVANCED_QUERY_JSON = """
{{
    "srtDirection": "DESC",
    "pgNum": 0,
    "pgSize": 100,
    "srtKey": "CreatedAt",
    "groups": [
        {{
            "filterClause": "OR",
            "filters": [
                {{
                    "value": "{state_1}",
                    "term": "state",
                    "operator": "IS"
                }},
                {{
                    "value": "{state_2}",
                    "term": "state",
                    "operator": "IS"
                }},
                {{
                    "value": "{state_3}",
                    "term": "state",
                    "operator": "IS"
                }}
            ]
        }},
        {{
            "filterClause": "OR",
            "filters": [
                {{
                    "value": "{actor}",
                    "term": "actor",
                    "operator": "CONTAINS"
                }}
            ]
        }},
        {{
            "filterClause": "AND",
            "filters": [
                {{
                    "value": "{on_or_after}",
                    "term": "createdAt",
                    "operator": "ON_OR_AFTER"
                }},
                {{
                    "value": "{on_or_before}",
                    "term": "createdAt",
                    "operator": "ON_OR_BEFORE"
                }}
            ]
        }},
        {{
            "filterClause": "OR",
            "filters": [
                {{
                    "value": "{rule_id}",
                    "term": "ruleId",
                    "operator": "IS"
                }}
            ]
        }}
    ],
    "groupClause": "AND"
}}""".format(
    **ADVANCED_QUERY_VALUES
)
advanced_query_incompat_test_params = pytest.mark.parametrize(
    "arg",
    [
        ("--begin", "1d"),
        ("--end", "1d"),
        ("--severity", "HIGH"),
        ("--actor", "test"),
        ("--actor-contains", "test"),
        ("--exclude-actor", "test"),
        ("--exclude-actor-contains", "test"),
        ("--rule-name", "test"),
        ("--exclude-rule-name", "test"),
        ("--rule-id", "test"),
        ("--exclude-rule-id", "test"),
        ("--rule-type", "FedEndpointExfiltration"),
        ("--exclude-rule-type", "FedEndpointExfiltration"),
        ("--description", "test"),
        ("--state", "OPEN"),
    ],
)
ALERT_DETAILS_FULL_RESPONSE = {
    "type$": "ALERT_DETAILS_RESPONSE",
    "alerts": [
        {
            "type$": "ALERT_DETAILS",
            "tenantId": "11111111-2222-3333-4444-55559a126666",
            "type": "FED_ENDPOINT_EXFILTRATION",
            "name": "Some Burp Suite Test Rule",
            "description": "Some Burp Rule",
            "actor": "neilwin0415@code42.com",
            "actorId": "1002844444570300000",
            "target": "N/A",
            "severity": "HIGH",
            "ruleId": "e9bfa082-4541-4432-aacd-d8b2ca074762",
            "ruleSource": "Alerting",
            "id": "TEST-ALERT-ID-123",
            "createdAt": "2021-04-23T21:18:59.2032940Z",
            "state": "PENDING",
            "stateLastModifiedBy": "test@example.com",
            "stateLastModifiedAt": "2021-04-26T12:37:30.4605390Z",
            "observations": [
                {
                    "type$": "OBSERVATION",
                    "id": "f561e556-a746-4db0-b99b-71546adf57c4",
                    "observedAt": "2021-04-23T21:10:00.0000000Z",
                    "type": "FedEndpointExfiltration",
                    "data": {
                        "type$": "OBSERVED_ENDPOINT_ACTIVITY",
                        "id": "f561e556-a746-4db0-b99b-71546adf57c4",
                        "sources": ["Endpoint"],
                        "exposureTypes": ["ApplicationRead"],
                        "firstActivityAt": "2021-04-23T21:10:00.0000000Z",
                        "lastActivityAt": "2021-04-23T21:15:00.0000000Z",
                        "fileCount": 1,
                        "totalFileSize": 8326,
                        "fileCategories": [
                            {
                                "type$": "OBSERVED_FILE_CATEGORY",
                                "category": "Image",
                                "fileCount": 1,
                                "totalFileSize": 8326,
                                "isSignificant": False,
                            }
                        ],
                        "files": [
                            {
                                "type$": "OBSERVED_FILE",
                                "eventId": "0_c4e43418-07d9-4a9f-a138-29f39a124d33_1002847122023325984_4b6d298c-8660-4cb8-b6d1-61d09a5c69ba_0",
                                "path": "C:\\Users\\Test Testerson\\Downloads",
                                "name": "mad cat - Copy.jpg",
                                "category": "Image",
                                "size": 8326,
                            }
                        ],
                        "syncToServices": [],
                        "sendingIpAddresses": ["174.20.92.47"],
                        "appReadDetails": [
                            {
                                "type$": "APP_READ_DETAILS",
                                "tabTitles": [
                                    "file.example.com - Super simple file sharing - Google Chrome"
                                ],
                                "tabUrl": "https://www.file.example.com/",
                                "tabInfos": [
                                    {
                                        "type$": "TAB_INFO",
                                        "tabUrl": "https://www.file.example.com/",
                                        "tabTitle": "example - Super simple file sharing - Google Chrome",
                                    }
                                ],
                                "destinationCategory": "Uncategorized",
                                "destinationName": "Uncategorized",
                                "processName": "\\Device\\HarddiskVolume3\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                            }
                        ],
                    },
                }
            ],
            "note": {
                "type$": "NOTE",
                "id": "72f8cd62-5cb8-4896-947d-f07e17053eaf",
                "lastModifiedAt": "2021-04-26T12:37:30.4987600Z",
                "lastModifiedBy": "test@example.com",
                "message": "TEST-NOTE-CLI-UNIT-TESTS",
            },
        }
    ],
}
search_and_send_to_test = get_mark_for_search_and_send_to("alerts")


@pytest.fixture
def alert_cursor_with_checkpoint(mocker):
    mock = mocker.patch(f"{PRODUCT_NAME}.cmds.alerts._get_alert_cursor_store")
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    mock.expected_datetime = "2020-01-20 06:00:00"
    return mock


@pytest.fixture
def alert_cursor_without_checkpoint(mocker):
    mock = mocker.patch(f"{PRODUCT_NAME}.cmds.alerts._get_alert_cursor_store")
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch(f"{PRODUCT_NAME}.cmds.alerts.convert_datetime_to_timestamp")
    mock.return_value = BEGIN_TIMESTAMP
    mock.expected_timestamp = "2020-01-01T06:00:00.000000Z"
    return mock


@pytest.fixture
def send_to_logger_factory(mocker):
    return mocker.patch("code42cli.cmds.search._try_get_logger_for_server")


@pytest.fixture
def full_alert_details_response(mocker):
    return create_mock_response(mocker, data=ALERT_DETAILS_FULL_RESPONSE)


@pytest.fixture
def mock_alert_search_response(mocker):
    data = json.dumps(
        {
            "type$": "ALERT_QUERY_RESPONSE",
            "alerts": [
                {
                    "tenantId": "MyExampleTenant",
                    "type": "FED_ENDPOINT_EXFILTRATION",
                    "name": "Removable Media Exfiltration Rule",
                    "description": "Alert me on all removable media exfiltration.",
                    "actor": "exampleUser@mycompany.com",
                    "actorId": "authorityUserId",
                    "target": "string",
                    "severity": "LOW",
                    "notificationInfo": [],
                    "ruleId": "uniqueRuleId",
                    "ruleSource": "Departing Employee",
                    "id": "alertId",
                    "createdAt": "2020-02-19T01:57:45.006683Z",
                    "state": "OPEN",
                    "stateLastModifiedBy": "string",
                    "stateLastModifiedAt": "2019-08-24T14:15:22Z",
                }
            ],
            "totalCount": "3",
            "problems": [],
        }
    )

    response1 = create_mock_response(mocker, data=data)
    response2 = create_mock_response(mocker, data=data)

    def response_gen():
        yield response1
        yield response2

    return response_gen()


@pytest.fixture
def search_all_alerts_success(cli_state, mock_alert_search_response):
    cli_state.sdk.alerts.search_all_pages.return_value = mock_alert_search_response


@search_and_send_to_test
def test_search_and_send_to_passes_query_object_when_searching_file_events(
    runner, cli_state, command, search_all_alerts_success
):
    runner.invoke(
        cli, [*command, "--advanced-query", ADVANCED_QUERY_JSON], obj=cli_state
    )

    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert isinstance(query, AlertQuery)


@search_and_send_to_test
def test_search_and_send_to_when_advanced_query_passed_as_json_string_builds_expected_query(
    cli_state, runner, command, search_all_alerts_success
):
    runner.invoke(
        cli, [*command, "--advanced-query", ADVANCED_QUERY_JSON], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    passed_filter_groups = query._filter_group_list
    expected_actor_filter = f.Actor.contains(ADVANCED_QUERY_VALUES["actor"])
    expected_actor_filter.filter_clause = "OR"
    expected_timestamp_filter = f.DateObserved.in_range(
        ADVANCED_QUERY_VALUES["on_or_after_timestamp"],
        ADVANCED_QUERY_VALUES["on_or_before_timestamp"],
    )
    expected_state_filter = f.AlertState.is_in(
        [
            ADVANCED_QUERY_VALUES["state_1"],
            ADVANCED_QUERY_VALUES["state_2"],
            ADVANCED_QUERY_VALUES["state_3"],
        ]
    )
    expected_rule_id_filter = f.RuleId.eq(ADVANCED_QUERY_VALUES["rule_id"])
    expected_rule_id_filter.filter_clause = "OR"
    assert expected_actor_filter in passed_filter_groups
    assert expected_timestamp_filter in passed_filter_groups
    assert expected_state_filter in passed_filter_groups
    assert expected_rule_id_filter in passed_filter_groups


@advanced_query_incompat_test_params
def test_search_with_advanced_query_and_incompatible_argument_errors(
    arg, cli_state, runner
):

    result = runner.invoke(
        cli,
        ["alerts", "search", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert f"{arg[0]} can't be used with: --advanced-query" in result.output


@advanced_query_incompat_test_params
def test_send_to_with_advanced_query_and_incompatible_argument_errors(
    arg, cli_state, runner
):

    result = runner.invoke(
        cli,
        ["alerts", "send-to", "0.0.0.0", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert f"{arg[0]} can't be used with: --advanced-query" in result.output


@search_and_send_to_test
def test_search_and_send_to_when_given_begin_and_end_dates_uses_expected_query(
    cli_state, runner, command, search_all_alerts_success
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)

    runner.invoke(
        cli, [*command, "--begin", begin_date, "--end", end_date], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}

    actual_begin = query_dict["groups"][0]["filters"][0]["value"]
    expected_begin = f"{begin_date}T00:00:00.000000Z"

    actual_end = query_dict["groups"][0]["filters"][1]["value"]
    expected_end = f"{end_date}T23:59:59.999999Z"

    assert actual_begin == expected_begin
    assert actual_end == expected_end


@search_and_send_to_test
def test_search_when_given_begin_and_end_date_and_times_uses_expected_query(
    cli_state, runner, command, search_all_alerts_success
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33:02"
    runner.invoke(
        cli,
        [*command, "--begin", f"{begin_date} {time}", "--end", f"{end_date} {time}"],
        obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}

    actual_begin = query_dict["groups"][0]["filters"][0]["value"]
    expected_begin = f"{begin_date}T{time}.000000Z"

    actual_end = query_dict["groups"][0]["filters"][1]["value"]
    expected_end = f"{end_date}T{time}.000000Z"

    assert actual_begin == expected_begin
    assert actual_end == expected_end


@search_and_send_to_test
def test_search_when_given_begin_date_and_time_without_seconds_uses_expected_query(
    cli_state, runner, command, search_all_alerts_success
):
    date = get_test_date_str(days_ago=89)
    time = "15:33"
    runner.invoke(cli, [*command, "--begin", f"{date} {time}"], obj=cli_state)
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}
    actual = query_dict["groups"][0]["filters"][0]["value"]
    expected = f"{date}T{time}:00.000000Z"
    assert actual == expected


@search_and_send_to_test
def test_search_and_send_to_when_given_end_date_and_time_uses_expected_query(
    cli_state, runner, command, search_all_alerts_success
):
    begin_date = get_test_date_str(days_ago=10)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33"
    runner.invoke(
        cli,
        [*command, "--begin", begin_date, "--end", f"{end_date} {time}"],
        obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}
    actual = query_dict["groups"][0]["filters"][1]["value"]
    expected = f"{end_date}T{time}:00.000000Z"
    assert actual == expected


@search_and_send_to_test
def test_search_and_send_to_when_given_begin_date_more_than_ninety_days_back_errors(
    cli_state, runner, command
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    result = runner.invoke(cli, [*command, "--begin", begin_date], obj=cli_state)
    assert "must be within 90 days" in result.output
    assert result.exit_code == 2


@search_and_send_to_test
def test_search_and_send_to_when_given_begin_date_and_not_use_checkpoint_and_cursor_exists_uses_begin_date(
    cli_state, runner, command, search_all_alerts_success
):
    begin_date = get_test_date_str(days_ago=1)
    runner.invoke(cli, [*command, "--begin", begin_date], obj=cli_state)
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}
    actual_ts = query_dict["groups"][0]["filters"][0]["value"]
    expected_ts = f"{begin_date}T00:00:00.000000Z"
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(query, f.DateObserved._term)


@search_and_send_to_test
def test_search_and_send_to_when_end_date_is_before_begin_date_causes_exit(
    cli_state, runner, command
):
    begin_date = get_test_date_str(days_ago=1)
    end_date = get_test_date_str(days_ago=3)
    result = runner.invoke(
        cli, [*command, "--begin", begin_date, "--end", end_date], obj=cli_state,
    )
    assert result.exit_code == 2
    assert "'--begin': cannot be after --end date" in result.output


@search_and_send_to_test
def test_search_and_send_to_with_only_begin_calls_search_all_alerts_with_expected_filters(
    cli_state, begin_option, runner, command, search_all_alerts_success
):
    res = runner.invoke(cli, [*command, "--begin", "1d"], obj=cli_state)
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}
    expected_filter_groups = [
        {
            "filterClause": "AND",
            "filters": [
                {
                    "operator": "ON_OR_AFTER",
                    "term": "createdAt",
                    "value": begin_option.expected_timestamp,
                }
            ],
        }
    ]
    assert res.exit_code == 0
    assert query_dict["groups"] == expected_filter_groups


@search_and_send_to_test
def test_search_and_send_to_with_use_checkpoint_and_without_begin_and_without_stored_checkpoint_causes_expected_error(
    cli_state, alert_cursor_without_checkpoint, runner, command
):
    result = runner.invoke(cli, [*command, "--use-checkpoint", "test"], obj=cli_state)
    assert result.exit_code == 2
    assert (
        "--begin date is required for --use-checkpoint when no checkpoint exists yet."
        in result.output
    )


@search_and_send_to_test
def test_search_and_send_to_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_search_all_alerts_with_begin_date(
    cli_state,
    begin_option,
    alert_cursor_without_checkpoint,
    runner,
    command,
    search_all_alerts_success,
):
    res = runner.invoke(
        cli, [*command, "--use-checkpoint", "test", "--begin", "1d"], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    query_dict = {k: v for k, v in query}
    actual_begin = query_dict["groups"][0]["filters"][0]["value"]

    assert res.exit_code == 0
    assert len(query._filter_group_list) == 1
    assert begin_option.expected_timestamp == actual_begin


@search_and_send_to_test
def test_search_and_send_to_with_use_checkpoint_and_with_begin_and_with_stored_checkpoint_calls_search_all_alerts_with_checkpoint_and_ignores_begin_arg(
    cli_state, alert_cursor_with_checkpoint, runner, command, search_all_alerts_success
):
    result = runner.invoke(
        cli, [*command, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert result.exit_code == 0
    assert len(query._filter_group_list) == 1
    assert (
        f"checkpoint of {alert_cursor_with_checkpoint.expected_datetime} exists"
        in result.output
    )


@search_and_send_to_test
def test_search_and_send_to_when_given_actor_is_uses_username_filter(
    cli_state, runner, command, search_all_alerts_success
):
    actor_name = "test.testerson"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--actor", actor_name], obj=cli_state
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.Actor.is_in([actor_name]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_actor_uses_actor_filter(
    cli_state, runner, command, search_all_alerts_success
):
    actor_name = "test.testerson"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--exclude-actor", actor_name], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.Actor.not_in([actor_name]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_rule_name_uses_rule_name_filter(
    cli_state, runner, command, search_all_alerts_success
):
    rule_name = "departing employee"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--rule-name", rule_name], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.RuleName.is_in([rule_name]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_rule_name_uses_rule_name_not_filter(
    cli_state, runner, command, search_all_alerts_success
):
    rule_name = "departing employee"
    runner.invoke(
        cli,
        [*command, "--begin", "1h", "--exclude-rule-name", rule_name],
        obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.RuleName.not_in([rule_name]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_rule_type_uses_rule_name_filter(
    cli_state, runner, command, search_all_alerts_success
):
    rule_type = "FedEndpointExfiltration"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--rule-type", rule_type], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.RuleType.is_in([rule_type]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_rule_type_uses_rule_name_not_filter(
    cli_state, runner, command, search_all_alerts_success
):
    rule_type = "FedEndpointExfiltration"
    runner.invoke(
        cli,
        [*command, "--begin", "1h", "--exclude-rule-type", rule_type],
        obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.RuleType.not_in([rule_type]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_rule_id_uses_rule_name_filter(
    cli_state, runner, command, search_all_alerts_success
):
    rule_id = "departing employee"
    runner.invoke(cli, [*command, "--begin", "1h", "--rule-id", rule_id], obj=cli_state)
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.RuleId.is_in([rule_id]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_rule_id_uses_rule_name_not_filter(
    cli_state, runner, command, search_all_alerts_success
):
    rule_id = "departing employee"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--exclude-rule-id", rule_id], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.RuleId.not_in([rule_id]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_description_uses_description_filter(
    cli_state, runner, command, search_all_alerts_success
):
    description = "test description"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--description", description], obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.Description.contains(description) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_when_given_multiple_search_args_uses_expected_filters(
    cli_state, runner, command, search_all_alerts_success
):
    actor = "test.testerson@example.com"
    exclude_actor = "flag.flagerson@example.com"
    rule_name = "departing employee"

    runner.invoke(
        cli,
        [
            *command,
            "--begin",
            "1h",
            "--actor",
            actor,
            "--exclude-actor",
            exclude_actor,
            "--rule-name",
            rule_name,
        ],
        obj=cli_state,
    )
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    assert f.Actor.is_in([actor]) in query._filter_group_list
    assert f.Actor.not_in([exclude_actor]) in query._filter_group_list
    assert f.RuleName.is_in([rule_name]) in query._filter_group_list


@search_and_send_to_test
def test_search_and_send_to_with_or_query_flag_produces_expected_query(
    runner, cli_state, command, search_all_alerts_success
):
    begin_date = get_test_date_str(days_ago=10)
    test_actor = "test@example.com"
    test_rule_type = "FedEndpointExfiltration"
    runner.invoke(
        cli,
        [
            *command,
            "--or-query",
            "--begin",
            begin_date,
            "--actor",
            test_actor,
            "--rule-type",
            test_rule_type,
        ],
        obj=cli_state,
    )
    expected_query = {
        "tenantId": None,
        "groupClause": "AND",
        "groups": [
            {
                "filterClause": "AND",
                "filters": [
                    {
                        "operator": "ON_OR_AFTER",
                        "term": "createdAt",
                        "value": f"{begin_date}T00:00:00.000000Z",
                    }
                ],
            },
            {
                "filterClause": "OR",
                "filters": [
                    {"operator": "IS", "term": "actor", "value": "test@example.com"},
                    {
                        "operator": "IS",
                        "term": "type",
                        "value": "FedEndpointExfiltration",
                    },
                ],
            },
        ],
        "pgNum": 0,
        "pgSize": 500,
        "srtDirection": "asc",
        "srtKey": "CreatedAt",
    }
    query = cli_state.sdk.alerts.search_all_pages.call_args.args[0]
    actual_query = {k: v for k, v in query}
    assert actual_query == expected_query


@search_and_send_to_test
def test_search_and_send_to_handles_error_expected_message_logged_and_printed(
    runner, cli_state, caplog, command
):
    exception_msg = "Test Exception"
    expected_msg = "Unknown problem occurred"
    cli_state.sdk.alerts.search_all_pages.side_effect = Exception(exception_msg)
    with caplog.at_level(logging.ERROR):
        result = runner.invoke(cli, [*command, "--begin", "1d"], obj=cli_state)
        assert "Error:" in result.output
        assert expected_msg in result.output
        assert exception_msg in caplog.text


@pytest.mark.parametrize(
    "protocol", (ServerProtocol.TLS_TCP, ServerProtocol.TLS_TCP, ServerProtocol.UDP)
)
def test_send_to_allows_protocol_arg(cli_state, runner, protocol):
    res = runner.invoke(
        cli,
        ["alerts", "send-to", "0.0.0.0", "--begin", "1d", "--protocol", protocol],
        obj=cli_state,
    )
    assert res.exit_code == 0


def test_send_to_when_given_unknown_protocol_fails(cli_state, runner):
    res = runner.invoke(
        cli,
        ["alerts", "send-to", "0.0.0.0", "--begin", "1d", "--protocol", "ATM"],
        obj=cli_state,
    )
    assert res.exit_code


def test_send_to_certs_and_ignore_cert_validation_args_are_incompatible(
    cli_state, runner
):
    res = runner.invoke(
        cli,
        [
            "alerts",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            "TLS-TCP",
            "--certs",
            "certs/file",
            "--ignore-cert-validation",
        ],
        obj=cli_state,
    )
    assert "Error: --ignore-cert-validation can't be used with: --certs" in res.output


def test_send_to_creates_expected_logger(cli_state, runner, send_to_logger_factory):
    runner.invoke(
        cli,
        [
            "alerts",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            "TLS-TCP",
            "--certs",
            "certs/file",
        ],
        obj=cli_state,
    )
    send_to_logger_factory.assert_called_once_with(
        "0.0.0.0", "TLS-TCP", "RAW-JSON", "certs/file"
    )


def test_send_to_when_given_ignore_cert_validation_uses_certs_equal_to_ignore_str(
    cli_state, runner, send_to_logger_factory
):
    runner.invoke(
        cli,
        [
            "alerts",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            "TLS-TCP",
            "--ignore-cert-validation",
        ],
        obj=cli_state,
    )
    send_to_logger_factory.assert_called_once_with(
        "0.0.0.0", "TLS-TCP", "RAW-JSON", "ignore"
    )


@pytest.mark.parametrize("protocol", (ServerProtocol.UDP, ServerProtocol.TCP))
def test_send_to_when_given_ignore_cert_validation_with_non_tls_protocol_fails_expectedly(
    cli_state, runner, protocol
):
    res = runner.invoke(
        cli,
        [
            "alerts",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            protocol,
            "--ignore-cert-validation",
        ],
        obj=cli_state,
    )
    assert (
        "'--ignore-cert-validation' can only be used with '--protocol TLS-TCP'"
        in res.output
    )


@pytest.mark.parametrize("protocol", (ServerProtocol.UDP, ServerProtocol.TCP))
def test_send_to_when_given_certs_with_non_tls_protocol_fails_expectedly(
    cli_state, runner, protocol
):
    res = runner.invoke(
        cli,
        [
            "alerts",
            "send-to",
            "0.0.0.0",
            "--begin",
            "1d",
            "--protocol",
            protocol,
            "--certs",
            "certs.pem",
        ],
        obj=cli_state,
    )
    assert "'--certs' can only be used with '--protocol TLS-TCP'" in res.output


def test_get_alert_details_batches_results_according_to_batch_size(sdk):
    alerts._ALERT_DETAIL_BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    alerts._get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert sdk.alerts.get_details.call_count == 10


def test_get_alert_details_sorts_results_by_date(sdk):
    alerts._ALERT_DETAIL_BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    results = alerts._get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert results == SORTED_ALERT_DETAILS


#
def test_show_outputs_expected_headers(cli_state, runner, full_alert_details_response):
    cli_state.sdk.alerts.get_details.return_value = full_alert_details_response
    result = runner.invoke(cli, ["alerts", "show", "TEST-ALERT-ID"], obj=cli_state)
    assert "Id" in result.output
    assert "RuleName" in result.output
    assert "Username" in result.output
    assert "ObservedDate" in result.output
    assert "State" in result.output
    assert "Severity" in result.output
    assert "Description" in result.output


def test_show_outputs_expected_values(cli_state, runner, full_alert_details_response):
    cli_state.sdk.alerts.get_details.return_value = full_alert_details_response
    result = runner.invoke(cli, ["alerts", "show", "TEST-ALERT-ID"], obj=cli_state)
    # Values found in ALERT_DETAILS_FULL_RESPONSE.
    assert "TEST-ALERT-ID-123" in result.output
    assert "Some Burp Suite Test Rule" in result.output
    assert "neilwin0415@code42.com" in result.output
    assert "2021-04-23T21:18:59.2032940Z" in result.output
    assert "PENDING" in result.output
    assert "HIGH" in result.output
    assert "Some Burp Rule" in result.output


def test_show_when_alert_has_note_includes_note(
    cli_state, runner, full_alert_details_response
):
    cli_state.sdk.alerts.get_details.return_value = full_alert_details_response
    result = runner.invoke(cli, ["alerts", "show", "TEST-ALERT-ID"], obj=cli_state)
    # Note is included in `full_alert_details_response` initially.
    assert "Note" in result.output
    assert "TEST-NOTE-CLI-UNIT-TESTS" in result.output


def test_show_when_alert_has_no_note_excludes_note(
    mocker, cli_state, runner, full_alert_details_response
):
    response_data = dict(ALERT_DETAILS_FULL_RESPONSE)
    response_data["alerts"][0]["note"] = None
    cli_state.sdk.alerts.get_details.return_value = create_mock_response(
        mocker, data=response_data
    )
    result = runner.invoke(cli, ["alerts", "show", "TEST-ALERT-ID"], obj=cli_state)
    # Note is included in `full_alert_details_response` initially.
    assert "Note" not in result.output


def test_show_when_alert_not_found_output_expected_error_message(
    cli_state, runner, custom_error
):
    cli_state.sdk.alerts.get_details.side_effect = Py42NotFoundError(custom_error)
    result = runner.invoke(cli, ["alerts", "show", "TEST-ALERT-ID"], obj=cli_state)
    assert "No alert found with ID 'TEST-ALERT-ID'." in result.output


def test_show_when_alert_has_observations_and_includes_observations_outputs_observations(
    cli_state, runner, full_alert_details_response
):
    cli_state.sdk.alerts.get_details.return_value = full_alert_details_response
    result = runner.invoke(
        cli,
        ["alerts", "show", "TEST-ALERT-ID", "--include-observations"],
        obj=cli_state,
    )
    assert "Observations:" in result.output
    assert "OBSERVATION" in result.output
    assert "f561e556-a746-4db0-b99b-71546adf57c4" in result.output
    assert "observedAt" in result.output
    assert "FedEndpointExfiltration" in result.output


def test_show_when_alert_has_observations_and_excludes_observations_does_not_output_observations(
    cli_state, runner, full_alert_details_response
):
    cli_state.sdk.alerts.get_details.return_value = full_alert_details_response
    result = runner.invoke(cli, ["alerts", "show", "TEST-ALERT-ID"], obj=cli_state)
    assert "Observations:" not in result.output


def test_show_when_alert_does_not_have_observations_and_includes_observations_outputs_no_observations(
    mocker, cli_state, runner
):
    response_data = dict(ALERT_DETAILS_FULL_RESPONSE)
    response_data["alerts"][0]["observations"] = None
    cli_state.sdk.alerts.get_details.return_value = create_mock_response(
        mocker, data=response_data
    )
    result = runner.invoke(
        cli,
        ["alerts", "show", "TEST-ALERT-ID", "--include-observations"],
        obj=cli_state,
    )
    assert "No observations found" in result.output
    assert "Observations:" not in result.output
    assert "FedEndpointExfiltration" not in result.output


def test_update_when_given_state_calls_py42_update_state(cli_state, runner):
    runner.invoke(
        cli,
        ["alerts", "update", "TEST-ALERT-ID", "--state", AlertState.PENDING],
        obj=cli_state,
    )
    cli_state.sdk.alerts.update_state.assert_called_once_with(
        AlertState.PENDING, ["TEST-ALERT-ID"], note=None
    )


def test_update_when_given_state_and_note_calls_py42_update_state_and_includes_note(
    cli_state, runner
):
    runner.invoke(
        cli,
        [
            "alerts",
            "update",
            "TEST-ALERT-ID",
            "--state",
            AlertState.PENDING,
            "--note",
            "test-note",
        ],
        obj=cli_state,
    )
    cli_state.sdk.alerts.update_state.assert_called_once_with(
        AlertState.PENDING, ["TEST-ALERT-ID"], note="test-note"
    )


def test_update_when_given_note_and_not_state_calls_py42_update_note(cli_state, runner):
    runner.invoke(
        cli,
        ["alerts", "update", "TEST-ALERT-ID", "--note", "test-note"],
        obj=cli_state,
    )
    cli_state.sdk.alerts.update_note.assert_called_once_with(
        "TEST-ALERT-ID", "test-note"
    )


def test_bulk_update_uses_expected_arguments(runner, mocker, cli_state_with_user):
    bulk_processor = mocker.patch("code42cli.cmds.alerts.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_update.csv", "w") as csv:
            csv.writelines(
                ["id,state,note\n", "1,PENDING,note1\n", "2,IN_PROGRESS,note2\n"]
            )
        runner.invoke(
            cli,
            ["alerts", "bulk", "update", "test_update.csv"],
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == [
        {"id": "1", "state": "PENDING", "note": "note1"},
        {"id": "2", "state": "IN_PROGRESS", "note": "note2"},
    ]
