import pytest
from click.testing import CliRunner

from c42eventextractor.extractors import AlertExtractor
from py42.sdk.queries.alerts.filters import *

from code42cli import PRODUCT_NAME
from code42cli.main import cli
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.cmds.search import extraction

from tests.cmds.conftest import get_filter_value_from_json
from ..conftest import get_test_date_str


BEGIN_TIMESTAMP = 1577858400.0
END_TIMESTAMP = 1580450400.0
CURSOR_TIMESTAMP = 1579500000.0


ALERT_SUMMARY_LIST = [{"id": i} for i in range(20)]

ALERT_DETAIL_RESULT = [
    {"alerts": [{"id": 1, "createdAt": "2020-01-17"}, {"id": 11, "createdAt": "2020-01-18"}]},
    {"alerts": [{"id": 2, "createdAt": "2020-01-19"}, {"id": 12, "createdAt": "2020-01-20"}]},
    {"alerts": [{"id": 3, "createdAt": "2020-01-01"}, {"id": 13, "createdAt": "2020-01-02"}]},
    {"alerts": [{"id": 4, "createdAt": "2020-01-03"}, {"id": 14, "createdAt": "2020-01-04"}]},
    {"alerts": [{"id": 5, "createdAt": "2020-01-05"}, {"id": 15, "createdAt": "2020-01-06"}]},
    {"alerts": [{"id": 6, "createdAt": "2020-01-07"}, {"id": 16, "createdAt": "2020-01-08"}]},
    {"alerts": [{"id": 7, "createdAt": "2020-01-09"}, {"id": 17, "createdAt": "2020-01-10"}]},
    {"alerts": [{"id": 8, "createdAt": "2020-01-11"}, {"id": 18, "createdAt": "2020-01-12"}]},
    {"alerts": [{"id": 9, "createdAt": "2020-01-13"}, {"id": 19, "createdAt": "2020-01-14"}]},
    {"alerts": [{"id": 10, "createdAt": "2020-01-15"}, {"id": 20, "createdAt": "2020-01-16"}]},
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


@pytest.fixture
def stdout_logger(mocker):
    mock = mocker.patch("{}.cmds.search.logger_factory.get_logger_for_stdout".format(PRODUCT_NAME))
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def server_logger(mocker):
    mock = mocker.patch("{}.cmds.search.logger_factory.get_logger_for_server".format(PRODUCT_NAME))
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def file_logger(mocker):
    mock = mocker.patch("{}.cmds.search.logger_factory.get_logger_for_file".format(PRODUCT_NAME))
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def alert_extractor(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_extractor")
    mock.return_value = mocker.MagicMock(spec=AlertExtractor)
    return mock


@pytest.fixture
def alert_cursor_with_checkpoint(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_cursor_store")
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def alert_cursor_without_checkpoint(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_cursor_store")
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch("code42cli.cmds.search.options.parse_min_timestamp")
    mock.return_value = BEGIN_TIMESTAMP
    return mock


@pytest.fixture
def alert_extract_func(mocker):
    return mocker.patch("code42cli.cmds.alerts._extract")


@pytest.fixture
def alert_extractor(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_extractor")
    mock.return_value = mocker.MagicMock(spec=AlertExtractor)
    return mock.return_value


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


ADVANCED_QUERY_JSON = '{"some": "complex json"}'


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_is_advanced_query_uses_only_the_extract_advanced_method(
    cmd, cli_state, alert_extractor
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--advanced-query", ADVANCED_QUERY_JSON], obj=cli_state
    )
    alert_extractor.extract_advanced.assert_called_once_with('{"some": "complex json"}')
    assert alert_extractor.extract.call_count == 0


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_is_advanced_query_and_has_begin_date_exits(cmd, cli_state):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alerts", *cmd, "--advanced-query", ADVANCED_QUERY_JSON, "--begin", "1d"],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "--begin can't be used with: --advanced-query" in result.output


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_advanced_query_and_has_begin_date_exits(cmd, cli_state):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alerts", *cmd, "--advanced-query", ADVANCED_QUERY_JSON, "--end", "1d"],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "--end can't be used with: --advanced-query" in result.output


@pytest.mark.parametrize(
    "arg",
    [
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
        ("--use-checkpoint", "test"),
    ],
)
def test_print_when_advanced_query_and_other_incompatible_argument_passed(arg, cli_state):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", "print", "--advanced-query", ADVANCED_QUERY_JSON, *arg], obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@pytest.mark.parametrize(
    "arg",
    [
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
        ("--use-checkpoint", "test"),
    ],
)
def test_write_to_when_advanced_query_and_other_incompatible_argument_passed(arg, cli_state):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alerts", "write-to", "test_file", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@pytest.mark.parametrize(
    "arg",
    [
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
        ("--use-checkpoint", "test"),
    ],
)
def test_send_to_when_advanced_query_and_other_incompatible_argument_passed(arg, cli_state):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alerts", "send-to", "localhost", "--advanced-query", ADVANCED_QUERY_JSON, *arg],
        obj=cli_state,
    )
    assert result.exit_code == 2
    assert "{} can't be used with: --advanced-query".format(arg[0]) in result.output


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_begin_and_end_dates_uses_expected_query(cmd, cli_state, alert_extractor):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "print", "--begin", begin_date, "--end", end_date])
    filters = alert_extractor.extract.call_args[0][0]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{0}T00:00:00.000Z".format(begin_date)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{0}T23:59:59.999Z".format(end_date)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_begin_and_end_date_and_time_uses_expected_query(
    cmd, cli_state, alert_extractor
):
    begin_date = get_test_date_str(days_ago=89)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33:02"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "alerts",
            "print",
            "--begin",
            "{} {}".format(begin_date, time),
            "--end",
            "{} {}".format(end_date, time),
        ],
    )
    filters = alert_extractor.extract.call_args[0][0]
    actual_begin = get_filter_value_from_json(filters, filter_index=0)
    expected_begin = "{0}T{1}.000Z".format(begin_date, time)
    actual_end = get_filter_value_from_json(filters, filter_index=1)
    expected_end = "{0}T{1}.000Z".format(end_date, time)
    assert actual_begin == expected_begin
    assert actual_end == expected_end


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_begin_date_and_time_without_seconds_uses_expected_query(
    cmd, cli_state, alert_extractor
):
    date = get_test_date_str(days_ago=89)
    time = "15:33"
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "print", "--begin", "{} {}".format(date, time)])
    actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=0)
    expected = "{0}T{1}:00.000Z".format(date, time)
    assert actual == expected


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_end_date_and_time_uses_expected_query(cmd, cli_state, alert_extractor):
    begin_date = get_test_date_str(days_ago=10)
    end_date = get_test_date_str(days_ago=1)
    time = "15:33"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", "print", "--begin", begin_date, "--end", "{} {}".format(end_date, time)]
    )
    actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=1)
    expected = "{0}T{1}:00.000Z".format(end_date, time)
    assert actual == expected


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_begin_date_more_than_ninety_days_back_in_ad_hoc_mode_causes_exit(
    cmd, cli_state,
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", *cmd, "--begin", begin_date])
    assert result.exit_code == 2
    assert "must be within 90 days" in result.output


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_begin_date_past_90_days_and_use_checkpoint_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
    cmd, cli_state, alert_cursor_with_checkpoint, mocker, alert_extractor
):
    begin_date = get_test_date_str(days_ago=91) + " 12:51:00"
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", *cmd, "--begin", begin_date, "--use-checkpoint", "test"])
    assert not filter_term_is_in_call_args(alert_extractor, DateObserved._term)


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_begin_date_and_not_use_checkpoint_and_cursor_exists_uses_begin_date(
    cmd, cli_state, alert_extractor
):
    begin_date = get_test_date_str(days_ago=1)
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", *cmd, "--begin", begin_date])

    actual_ts = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=0)
    expected_ts = "{0}T00:00:00.000Z".format(begin_date)
    assert actual_ts == expected_ts
    assert filter_term_is_in_call_args(alert_extractor, DateObserved._term)


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_end_date_is_before_begin_date_causes_exit(cmd, cli_state):
    begin_date = get_test_date_str(days_ago=1)
    end_date = get_test_date_str(days_ago=3)
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", *cmd, "--begin", begin_date, "--end", end_date])
    assert result.exit_code == 2
    assert "'--begin': cannot be after --end date" in result.output


def test_get_alert_details_batches_results_according_to_batch_size(sdk):
    extraction._ALERT_DETAIL_BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    results = extraction._get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert sdk.alerts.get_details.call_count == 10


def test_get_alert_details_sorts_results_by_date(sdk):
    extraction._ALERT_DETAIL_BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    results = extraction._get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert results == SORTED_ALERT_DETAILS


def test_print_with_only_begin_calls_extract_with_expected_args(
    mocker, cli_state, alert_extract_func, stdout_logger, begin_option
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "print", "--begin", "1h"], obj=cli_state)
    alert_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        checkpoint_name=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=stdout_logger.return_value,
    )
    assert result.exit_code == 0


def test_send_to_with_only_begin_calls_extract_with_expected_args(
    mocker, cli_state, alert_extract_func, server_logger, begin_option
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "send-to", "localhost", "--begin", "1h"], obj=cli_state)
    alert_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        checkpoint_name=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=server_logger.return_value,
    )
    assert result.exit_code == 0


def test_write_to_with_only_begin_calls_extract_with_expected_args(
    mocker, cli_state, alert_extract_func, file_logger, begin_option
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "write-to", "test_file", "--begin", "1h"], obj=cli_state)
    alert_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        checkpoint_name=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=file_logger.return_value,
    )
    assert result.exit_code == 0


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_with_use_checkpoint_and_without_begin_and_without_checkpoint_causes_expected_error(
    cmd, cli_state, alert_cursor_without_checkpoint
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", *cmd, "--use-checkpoint", "test"], obj=cli_state)
    assert result.exit_code == 2
    assert (
        "--begin date is required for --use-checkpoint when no checkpoint exists yet."
        in result.output
    )


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    cmd,
    cli_state,
    alert_extract_func,
    begin_option,
    alert_cursor_without_checkpoint,
    stdout_logger,
    server_logger,
    file_logger,
    mocker,
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    alert_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=alert_cursor_without_checkpoint.return_value,
        checkpoint_name="test",
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=mocker.ANY,
    )


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_with_use_checkpoint_and_with_begin_and_with_checkpoint_calls_extract_with_begin_date_none(
    cmd,
    cli_state,
    alert_extract_func,
    alert_cursor_with_checkpoint,
    stdout_logger,
    server_logger,
    file_logger,
    mocker,
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--use-checkpoint", "test", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    alert_extract_func.assert_called_with(
        sdk=cli_state.sdk,
        cursor=alert_cursor_with_checkpoint.return_value,
        checkpoint_name="test",
        filter_list=cli_state.search_filters,
        begin=None,
        end=None,
        advanced_query=None,
        output_logger=mocker.ANY,
    )
    assert "checkpoint of 2020-01-20T06:00:00+00:00 exists" in result.output


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_actor_is_uses_username_filter(cmd, cli_state, alert_extractor):
    actor_name = "test.testerson"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--actor", actor_name], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(Actor.is_in([actor_name])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_exclude_actor_uses_actor_filter(cmd, cli_state, alert_extractor):
    actor_name = "test.testerson"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--exclude-actor", actor_name], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(Actor.not_in([actor_name])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_rule_name_uses_rule_name_filter(cmd, cli_state, alert_extractor):
    rule_name = "departing employee"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--rule-name", rule_name], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(RuleName.is_in([rule_name])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_exclude_rule_name_uses_rule_name_not_filter(cmd, cli_state, alert_extractor):
    rule_name = "departing employee"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--exclude-rule-name", rule_name], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(RuleName.not_in([rule_name])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_rule_type_uses_rule_name_filter(cmd, cli_state, alert_extractor):
    rule_type = "FedEndpointExfiltration"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--rule-type", rule_type], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(RuleType.is_in([rule_type])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_exclude_rule_type_uses_rule_name_not_filter(cmd, cli_state, alert_extractor):
    rule_type = "FedEndpointExfiltration"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--exclude-rule-type", rule_type], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(RuleType.not_in([rule_type])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_rule_id_uses_rule_name_filter(cmd, cli_state, alert_extractor):
    rule_id = "departing employee"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--rule-id", rule_id], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(RuleId.is_in([rule_id])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_exclude_rule_id_uses_rule_name_not_filter(cmd, cli_state, alert_extractor):
    rule_id = "departing employee"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--exclude-rule-id", rule_id], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(RuleId.not_in([rule_id])) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_description_uses_description_filter(cmd, cli_state, alert_extractor):
    description = "test description"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--begin", "1h", "--description", description], obj=cli_state
    )
    filter_strings = [str(arg) for arg in alert_extractor.extract.call_args[0]]
    assert str(Description.contains(description)) in filter_strings


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_when_given_multiple_search_args_uses_expected_filters(cmd, cli_state, alert_extractor):
    actor = "test.testerson@example.com"
    exclude_actor = "flag.flagerson@code42.com"
    rule_name = "departing employee"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "alerts",
            *cmd,
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
    assert str(Actor.is_in([actor])) in filter_strings
    assert str(Actor.not_in([exclude_actor])) in filter_strings
    assert str(RuleName.is_in([rule_name])) in filter_strings
