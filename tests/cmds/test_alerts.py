import pytest

from click.testing import CliRunner

from code42cli import PRODUCT_NAME
from code42cli.main import cli
from code42cli.cmds.search_shared.cursor_store import AlertCursorStore

BEGIN_TIMESTAMP = "1000"
END_TIMESTAMP = "2000"
CURSOR_TIMESTAMP = "1500"


@pytest.fixture
def stdout_logger(mocker):
    mock = mocker.patch(
        "{}.cmds.search_shared.logger_factory.get_logger_for_stdout".format(PRODUCT_NAME)
    )
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def server_logger(mocker):
    mock = mocker.patch(
        "{}.cmds.search_shared.logger_factory.get_logger_for_server".format(PRODUCT_NAME)
    )
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def file_logger(mocker):
    mock = mocker.patch(
        "{}.cmds.search_shared.logger_factory.get_logger_for_file".format(PRODUCT_NAME)
    )
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture
def alert_cursor_with_checkpoint(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_cursor_store")
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get_stored_cursor_timestamp.return_value = CURSOR_TIMESTAMP
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def alert_cursor_without_checkpoint(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_cursor_store")
    mock_cursor = mocker.MagicMock(spec=AlertCursorStore)
    mock_cursor.get_stored_cursor_timestamp.return_value = None
    mock.return_value = mock_cursor
    return mock


@pytest.fixture
def begin_option(mocker):
    mock = mocker.patch("code42cli.cmds.search_shared.options.parse_min_timestamp")
    mock.return_value = BEGIN_TIMESTAMP
    return mock


@pytest.fixture
def alert_extractor(mocker):
    return mocker.patch("code42cli.cmds.alerts._extract")


def test_print_with_only_begin_calls_extract_with_expected_args(
    mocker, cli_state, alert_extractor, stdout_logger, begin_option
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "print", "--begin", "1h"], obj=cli_state)
    alert_extractor.assert_called_with(
        sdk=cli_state.sdk,
        cursor=None,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=stdout_logger.return_value,
    )
    assert result.exit_code == 0


def test_print_with_incremental_and_without_begin_and_without_checkpoint_causes_expected_error(
    cli_state, alert_cursor_without_checkpoint
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "print", "--incremental"], obj=cli_state)
    assert result.exit_code == 2
    assert (
        "--begin date is required for --incremental when no checkpoint exists yet." in result.output
    )


def test_send_to_with_incremental_and_without_begin_and_without_checkpoint_causes_expected_error(
    cli_state, alert_cursor_without_checkpoint, server_logger
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "send-to", "localhost", "--incremental"], obj=cli_state)
    assert result.exit_code == 2
    assert (
        "--begin date is required for --incremental when no checkpoint exists yet." in result.output
    )


def test_write_to_with_incremental_and_without_begin_and_without_checkpoint_causes_expected_error(
    cli_state, alert_cursor_without_checkpoint
):
    runner = CliRunner()
    result = runner.invoke(cli, ["alerts", "write-to", "test_file", "--incremental"], obj=cli_state)
    assert result.exit_code == 2
    assert (
        "--begin date is required for --incremental when no checkpoint exists yet." in result.output
    )


def test_print_with_incremental_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    cli_state, alert_extractor, begin_option, alert_cursor_without_checkpoint, stdout_logger,
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", "print", "--incremental", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    alert_extractor.assert_called_with(
        sdk=cli_state.sdk,
        cursor=alert_cursor_without_checkpoint.return_value,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=stdout_logger.return_value,
    )


def test_send_to_with_incremental_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    cli_state, alert_extractor, begin_option, alert_cursor_without_checkpoint, server_logger,
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", "send-to", "localhost", "--incremental", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    alert_extractor.assert_called_with(
        sdk=cli_state.sdk,
        cursor=alert_cursor_without_checkpoint.return_value,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=server_logger.return_value,
    )


def test_write_to_with_incremental_and_with_begin_and_without_checkpoint_calls_extract_with_begin_date(
    cli_state, alert_extractor, begin_option, alert_cursor_without_checkpoint, file_logger,
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", "write-to", "test_file", "--incremental", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    alert_extractor.assert_called_with(
        sdk=cli_state.sdk,
        cursor=alert_cursor_without_checkpoint.return_value,
        filter_list=cli_state.search_filters,
        begin=BEGIN_TIMESTAMP,
        end=None,
        advanced_query=None,
        output_logger=file_logger.return_value,
    )


def test_print_with_incremental_and_with_begin_and_with_checkpoint_calls_extract_with_begin_date_none(
    cli_state, alert_extractor, alert_cursor_with_checkpoint, stdout_logger,
):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["alerts", "print", "--incremental", "--begin", "1h"], obj=cli_state
    )
    assert result.exit_code == 0
    alert_extractor.assert_called_with(
        sdk=cli_state.sdk,
        cursor=alert_cursor_with_checkpoint.return_value,
        filter_list=cli_state.search_filters,
        begin=None,
        end=None,
        advanced_query=None,
        output_logger=stdout_logger.return_value,
    )
