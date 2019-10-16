import pytest
from argparse import Namespace
from datetime import datetime, timedelta

from py42 import settings
import py42.debug_level as debug_level
from c42seceventcli.aed import event_extraction_cli


@pytest.fixture
def mock_aed_extractor(mocker):
    return mocker.patch("c42secevents.extractors.AEDEventExtractor.extract")


@pytest.fixture
def mock_42(mocker):
    settings.verify_ssl_certs = True
    settings.debug_level = debug_level.NONE
    return mocker.patch("py42.sdk.SDK.create_using_local_account")


@pytest.fixture
def mock_arg_parse(mocker, mock_args):
    mock_parser = mocker.patch("argparse.ArgumentParser.parse_args")
    mock_parser.return_value = mock_args
    return mock_parser


@pytest.fixture
def mock_args():
    args = Namespace()
    args.c42_authority_url = "https://example.com"
    args.c42_username = "test.testerson@example.com"
    args.c42_begin_date = None
    args.c42_end_date = None
    args.c42_ignore_ssl_errors = None
    args.c42_output_format = None
    args.c42_record_cursor = None
    args.c42_exposure_types = None
    args.c42_debug_mode = None
    args.c42_destination_type = None
    args.c42_destination = None
    args.c42_syslog_port = None
    args.c42_syslog_protocol = None
    return args


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.patch("configparser.ConfigParser.read")


@pytest.fixture
def mock_config_get_arg(mocker):
    return mocker.patch("c42seceventcli.common.common.SecurityEventConfigParser.get")


@pytest.fixture
def mock_config_get_bool(mocker):
    return mocker.patch("c42seceventcli.common.common.SecurityEventConfigParser.get_bool")


@pytest.fixture
def mock_get_password(mocker):
    mock = mocker.patch("c42seceventcli.aed.event_extraction_cli.get_password")
    mock.get_password.return_value = "PASSWORD"
    return mock


def test_main_when_cli_arg_ignore_ssl_errors_is_true_that_py42_settings_verify_ssl_certs_is_false(
   mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_ignore_ssl_errors = True
    event_extraction_cli.main()
    assert not settings.verify_ssl_certs


def test_main_when_cli_arg_ignore_ssl_errors_is_false_that_py42_settings_verify_ssl_certs_to_true(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_ignore_ssl_errors = False
    event_extraction_cli.main()
    assert settings.verify_ssl_certs


def test_main_when_config_arg_ignore_ssl_errors_is_true_py42_settings_verify_ssl_certs_is_false(
    mock_42, mock_arg_parse, mock_aed_extractor, mock_config_parser, mock_get_password, mock_config_get_bool
):
    mock_config_get_bool.return_value = True
    event_extraction_cli.main()
    assert not settings.verify_ssl_certs


def test_main_when_config_arg_ignore_ssl_errors_is_false_py42_settings_verify_ssl_certs_is_true(
    mock_42, mock_arg_parse, mock_aed_extractor, mock_config_parser, mock_get_password, mock_config_get_bool
):
    mock_config_get_bool.return_value = False
    event_extraction_cli.main()
    assert settings.verify_ssl_certs


def test_main_when_cli_arg_debug_mode_is_true_that_py42_settings_debug_mode_is_debug(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_debug_mode = True
    event_extraction_cli.main()
    assert settings.debug_level == debug_level.DEBUG


def test_main_when_cli_arg_debug_mode_is_false_that_py42_settings_debug_mode_is_not_debug(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_debug_mode = False
    event_extraction_cli.main()
    assert settings.debug_level != debug_level.DEBUG


def test_main_when_config_arg_debug_mode_is_true_that_py42_settings_debug_mode_is_debug(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password, mock_config_get_bool
):
    mock_config_get_bool.return_value = True
    event_extraction_cli.main()
    assert settings.debug_level == debug_level.DEBUG


def test_main_when_config_arg_debug_mode_is_false_that_py42_settings_debug_mode_is_not_debug(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password, mock_config_get_bool
):
    mock_config_get_bool.return_value = False
    event_extraction_cli.main()
    assert settings.debug_level != debug_level.DEBUG


def test_main_when_cli_arg_begin_date_is_before_ninety_days_causes_program_exit(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_begin_date = "1970-10-31"
    with pytest.raises(SystemExit):
        event_extraction_cli.main()


def test_main_when_config_arg_begin_date_is_before_ninety_days_causes_program_exit(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password, mock_config_get_arg
):
    mock_config_get_arg.return_value = "1970-10-31"
    with pytest.raises(SystemExit):
        event_extraction_cli.main()


def test_main_when_cli_arg_begin_date_is_not_given_uses_min_timestamp_from_sixty_days_ago(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    event_extraction_cli.main()
    expected = ((datetime.now() - timedelta(days=60)) - datetime.utcfromtimestamp(0)).total_seconds()
    actual = mock_aed_extractor.call_args[0][0]
    assert pytest.approx(expected, actual)
