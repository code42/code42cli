import json

import py42.sdk.queries.alerts.filters as f
import pytest
from c42eventextractor.extractors import AlertExtractor
from tests.cmds.conftest import filter_term_is_in_call_args
from tests.cmds.conftest import get_filter_value_from_json
from tests.cmds.conftest import get_mark_for_search_and_send_to
from tests.conftest import get_test_date_str

from code42cli import PRODUCT_NAME
from code42cli.cmds.search import extraction
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
    "on_or_after": "2020-01-01T06:00:00.000Z",
    "on_or_after_timestamp": 1577858400.0,
    "on_or_before": "2020-02-01T06:00:00.000Z",
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
search_and_send_to_test = get_mark_for_search_and_send_to("alerts")


@pytest.fixture
def alert_extractor(mocker):
    mock = mocker.patch("{}.cmds.alerts._get_alert_extractor".format(PRODUCT_NAME))
    mock.return_value = mocker.MagicMock(spec=AlertExtractor)
    return mock.return_value


@pytest.fixture
def alert_cursor_with_checkpoint(mocker):
    mock = mocker.patch("{}.cmds.alerts._get_alert_cursor_store".format(PRODUCT_NAME))
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    mock.expected_timestamp = "2020-01-20T06:00:00+00:00"
    return mock


@pytest.fixture
def alert_cursor_without_checkpoint(mocker):
    mock = mocker.patch("{}.cmds.alerts._get_alert_cursor_store".format(PRODUCT_NAME))
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch(
        "{}.cmds.alerts.convert_datetime_to_timestamp".format(PRODUCT_NAME)
    )
    mock.return_value = BEGIN_TIMESTAMP
    mock.expected_timestamp = "2020-01-01T06:00:00.000Z"
    return mock


@pytest.fixture
def alert_extract_func(mocker):
    return mocker.patch("{}.cmds.alerts._extract".format(PRODUCT_NAME))


@pytest.fixture
def send_to_logger_factory(mocker):
    return mocker.patch("code42cli.cmds.search._try_get_logger_for_server")


@search_and_send_to_test
def test_search_and_send_to_when_advanced_query_passed_as_json_string_builds_expected_query(
    cli_state, alert_extractor, runner, command
):
    runner.invoke(
        cli, [*command, "--advanced-query", ADVANCED_QUERY_JSON], obj=cli_state,
    )
    passed_filter_groups = alert_extractor.extract.call_args[0]
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


@search_and_send_to_test
def test_search_and_send_to_without_advanced_query_uses_only_the_extract_method(
    cli_state, alert_extractor, runner, command
):

    runner.invoke(cli, [*command, "--begin", "1d"], obj=cli_state)
    assert alert_extractor.extract.call_count == 1
    assert alert_extractor.extract_advanced.call_count == 0


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
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


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
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@search_and_send_to_test
def test_search_and_send_to_when_given_begin_and_end_dates_uses_expected_query(
    cli_state, alert_extractor, runner, command
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)

    runner.invoke(
        cli, [*command, "--begin", begin_date, "--end", end_date], obj=cli_state,
    )
    filters = alert_extractor.extract.call_args[0][0]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{}T00:00:00.000Z".format(begin_date)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{}T23:59:59.999Z".format(end_date)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@search_and_send_to_test
def test_search_when_given_begin_and_end_date_and_times_uses_expected_query(
    cli_state, alert_extractor, runner, command
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33:02"
    runner.invoke(
        cli,
        [
            *command,
            "--begin",
            "{} {}".format(begin_date, time),
            "--end",
            "{} {}".format(end_date, time),
        ],
        obj=cli_state,
    )
    filters = alert_extractor.extract.call_args[0][0]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{}T{}.000Z".format(begin_date, time)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{}T{}.000Z".format(end_date, time)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@search_and_send_to_test
def test_search_when_given_begin_date_and_time_without_seconds_uses_expected_query(
    cli_state, alert_extractor, runner, command
):
    date = get_test_date_str(days_ago=89)
    time = "15:33"
    runner.invoke(cli, [*command, "--begin", "{} {}".format(date, time)], obj=cli_state)
    actual = get_filter_value_from_json(
        alert_extractor.extract.call_args[0][0], filter_index=0
    )
    expected = "{}T{}:00.000Z".format(date, time)
    assert actual == expected


@search_and_send_to_test
def test_search_and_send_to_when_given_end_date_and_time_uses_expected_query(
    cli_state, alert_extractor, runner, command
):
    begin_date = get_test_date_str(days_ago=10)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33"
    runner.invoke(
        cli,
        [*command, "--begin", begin_date, "--end", "{} {}".format(end_date, time)],
        obj=cli_state,
    )
    actual = get_filter_value_from_json(
        alert_extractor.extract.call_args[0][0], filter_index=1
    )
    expected = "{}T{}:00.000Z".format(end_date, time)
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
def test_search_and_send_to_when_given_begin_date_past_90_days_and_use_checkpoint_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    cli_state, alert_cursor_with_checkpoint, alert_extractor, runner, command
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    runner.invoke(
        cli,
        [*command, "--begin", begin_date, "--use-checkpoint", "test"],
        obj=cli_state,
    )
    assert not filter_term_is_in_call_args(alert_extractor, f.DateObserved._term)


@search_and_send_to_test
def test_search_and_send_to_when_given_begin_date_and_not_use_checkpoint_and_cursor_exists_uses_begin_date(
    cli_state, alert_extractor, runner, command
):
    begin_date = get_test_date_str(days_ago=1)
    runner.invoke(cli, [*command, "--begin", begin_date], obj=cli_state)
    actual_ts = get_filter_value_from_json(
        alert_extractor.extract.call_args[0][0], filter_index=0
    )
    expected_ts = "{}T00:00:00.000Z".format(begin_date)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(alert_extractor, f.DateObserved._term)


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
def test_search_and_send_to_with_only_begin_calls_extract_with_expected_filters(
    cli_state, alert_extractor, begin_option, runner, command
):
    res = runner.invoke(cli, [*command, "--begin", "1d"], obj=cli_state)
    assert res.exit_code == 0
    assert str(
        alert_extractor.extract.call_args[0][0]
    ) == '{{"filterClause":"AND", "filters":[{{"operator":"ON_OR_AFTER", "term":"createdAt", "value":"{}"}}]}}'.format(
        begin_option.expected_timestamp
    )


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
def test_search_and_send_to_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    cli_state,
    alert_extractor,
    begin_option,
    alert_cursor_without_checkpoint,
    runner,
    command,
):
    res = runner.invoke(
        cli, [*command, "--use-checkpoint", "test", "--begin", "1d"], obj=cli_state,
    )
    assert res.exit_code == 0
    assert len(alert_extractor.extract.call_args[0]) == 1
    assert begin_option.expected_timestamp in str(
        alert_extractor.extract.call_args[0][0]
    )


@search_and_send_to_test
def test_search_and_send_to_with_use_checkpoint_and_with_begin_and_with_stored_checkpoint_calls_extract_with_checkpoint_and_ignores_begin_arg(
    cli_state, alert_extractor, alert_cursor_with_checkpoint, runner, command
):

    result = runner.invoke(
        cli, [*command, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state,
    )
    assert result.exit_code == 0
    assert alert_extractor.extract.call_count == 1
    assert (
        "checkpoint of {} exists".format(
            alert_cursor_with_checkpoint.expected_timestamp
        )
        in result.output
    )


@search_and_send_to_test
def test_search_and_send_to_when_given_actor_is_uses_username_filter(
    cli_state, alert_extractor, runner, command
):
    actor_name = "test.testerson"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--actor", actor_name], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.Actor.is_in([actor_name])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_actor_uses_actor_filter(
    cli_state, alert_extractor, runner, command
):
    actor_name = "test.testerson"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--exclude-actor", actor_name], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.Actor.not_in([actor_name])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_rule_name_uses_rule_name_filter(
    cli_state, alert_extractor, runner, command
):
    rule_name = "departing employee"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--rule-name", rule_name], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.RuleName.is_in([rule_name])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_rule_name_uses_rule_name_not_filter(
    cli_state, alert_extractor, runner, command
):
    rule_name = "departing employee"
    runner.invoke(
        cli,
        [*command, "--begin", "1h", "--exclude-rule-name", rule_name],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.RuleName.not_in([rule_name])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_rule_type_uses_rule_name_filter(
    cli_state, alert_extractor, runner, command
):
    rule_type = "FedEndpointExfiltration"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--rule-type", rule_type], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.RuleType.is_in([rule_type])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_rule_type_uses_rule_name_not_filter(
    cli_state, alert_extractor, runner, command
):
    rule_type = "FedEndpointExfiltration"
    runner.invoke(
        cli,
        [*command, "--begin", "1h", "--exclude-rule-type", rule_type],
        obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.RuleType.not_in([rule_type])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_rule_id_uses_rule_name_filter(
    cli_state, alert_extractor, runner, command
):
    rule_id = "departing employee"
    runner.invoke(cli, [*command, "--begin", "1h", "--rule-id", rule_id], obj=cli_state)
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.RuleId.is_in([rule_id])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_exclude_rule_id_uses_rule_name_not_filter(
    cli_state, alert_extractor, runner, command
):
    rule_id = "departing employee"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--exclude-rule-id", rule_id], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.RuleId.not_in([rule_id])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_description_uses_description_filter(
    cli_state, alert_extractor, runner, command
):
    description = "test description"
    runner.invoke(
        cli, [*command, "--begin", "1h", "--description", description], obj=cli_state,
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.Description.contains(description)) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_when_given_multiple_search_args_uses_expected_filters(
    cli_state, alert_extractor, runner, command
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
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(f.Actor.is_in([actor])) in filter_strings
    assert str(f.Actor.not_in([exclude_actor])) in filter_strings
    assert str(f.RuleName.is_in([rule_name])) in filter_strings


@search_and_send_to_test
def test_search_and_send_to_with_or_query_flag_produces_expected_query(
    runner, cli_state, command
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
                        "value": "{}T00:00:00.000Z".format(begin_date),
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
    actual_query = json.loads(str(cli_state.sdk.alerts.search.call_args[0][0]))
    assert actual_query == expected_query


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
        "'--ignore-cert-validation' must be used with '--protocol TLS-TCP'"
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
    assert "'--certs' must be used with '--protocol TLS-TCP'" in res.output


def test_get_alert_details_batches_results_according_to_batch_size(sdk):
    extraction._ALERT_DETAIL_BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    extraction._get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert sdk.alerts.get_details.call_count == 10


def test_get_alert_details_sorts_results_by_date(sdk):
    extraction._ALERT_DETAIL_BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    results = extraction._get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert results == SORTED_ALERT_DETAILS
