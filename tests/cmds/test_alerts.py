import pytest
from click.testing import CliRunner

from c42eventextractor.extractors import AlertExtractor

from code42cli import PRODUCT_NAME
from code42cli.main import cli
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.cmds.search import extraction

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
    return mock


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


@pytest.mark.parametrize("cmd", [["print"], ["send-to", "localhost"], ["write-to", "test_file"]])
def test_alerts_when_is_advanced_query_uses_only_the_extract_advanced(
    cmd, cli_state, alert_extractor
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", *cmd, "--advanced-query", '{"some": "complex json"}'], obj=cli_state
    )
    alert_extractor.extract_advanced.assert_called_once_with('{"some": "complex json"}')
    assert alert_extractor.extract.call_count == 0


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
def test_alerts_with_use_checkpoint_and_without_begin_and_without_checkpoint_causes_expected_error(
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
def test_alerts_with_use_checkpoint_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
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
def test_alerts_with_use_checkpoint_and_with_begin_and_with_checkpoint_calls_extract_with_begin_date_none(
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
