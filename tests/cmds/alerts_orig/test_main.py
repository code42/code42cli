import pytest

import code42cli.cmds.alerts.main as main
from code42cli import PRODUCT_NAME


@pytest.fixture
def mock_logger_factory(mocker):
    return mocker.patch("{}.cmds.alerts.main.logger_factory".format(PRODUCT_NAME))


@pytest.fixture
def mock_extract(mocker):
    return mocker.patch("{}.cmds.alerts.main.extract".format(PRODUCT_NAME))


def test_print_out(sdk, profile, alert_namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_stdout.return_value = logger
    main.print_out(sdk, profile, alert_namespace)
    mock_extract.assert_called_with(sdk, profile, logger, alert_namespace)


def test_write_to(sdk, profile, alert_namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_file.return_value = logger
    main.write_to(sdk, profile, alert_namespace)
    mock_extract.assert_called_with(sdk, profile, logger, alert_namespace)


def test_send_to(sdk, profile, alert_namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_server.return_value = logger
    main.send_to(sdk, profile, alert_namespace)
    mock_extract.assert_called_with(sdk, profile, logger, alert_namespace)


def test_extract_when_is_advanced_query_and_has_begin_date_exits(sdk, profile, alert_namespace):
    alert_namespace.advanced_query = "some complex json"
    alert_namespace.begin = "begin date"
    with pytest.raises(SystemExit):
        main.send_to(sdk, profile, alert_namespace)


def test_extract_when_is_advanced_query_and_has_end_date_exits(sdk, profile, alert_namespace):
    alert_namespace.advanced_query = "some complex json"
    alert_namespace.end = "end date"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, alert_namespace)


@pytest.mark.parametrize(
    "arg",
    [
        "severity",
        "actor",
        "actor_contains",
        "exclude_actor",
        "exclude_actor_contains",
        "rule_name",
        "exclude_rule_name",
        "rule_id",
        "exclude_rule_id",
        "rule_type",
        "exclude_rule_type",
    ],
)
def test_extract_when_is_advanced_query_and_other_incompatible_multi_narg_argument_passed(
    sdk, profile, alert_namespace, arg
):
    alert_namespace.advanced_query = "some complex json"
    setattr(alert_namespace, arg, ["test_value"])
    with pytest.raises(SystemExit):
        main.write_to(sdk, profile, alert_namespace)


@pytest.mark.parametrize("arg", ["state", "description"])
def test_extract_when_is_advanced_query_and_other_incompatible_single_arg_argument_passed(
    sdk, profile, alert_namespace, arg
):
    alert_namespace.advanced_query = "some complex json"
    setattr(alert_namespace, arg, "test_value")
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, alert_namespace)


def test_extract_when_is_advanced_query_and_use_checkpoint_mode_exits(
    sdk, profile, alert_namespace
):
    alert_namespace.advanced_query = "some complex json"
    alert_namespace.use_checkpoint = "foo"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, alert_namespace)


def test_extract_when_is_advanced_query_and_does_not_use_checkpoint_does_not_exit(
    sdk, profile, alert_namespace, mock_extract, mocker, mock_logger_factory
):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_server.return_value = logger
    alert_namespace.advanced_query = "some complex json"
    alert_namespace.use_checkpoint = None
    main.print_out(sdk, profile, alert_namespace)
