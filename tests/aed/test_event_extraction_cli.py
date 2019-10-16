import pytest
from argparse import Namespace
from datetime import datetime, timedelta

from py42 import settings
import py42.debug_level as debug_level
from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter

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


@pytest.fixture
def mock_get_logger(mocker):
    return mocker.patch("c42seceventcli.aed.event_extraction_cli.get_logger")


@pytest.fixture
def mock_getpass(mocker):
    return mocker.patch("c42seceventcli.aed.event_extraction_cli.getpass")


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
    mock_42,
    mock_arg_parse,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_bool,
):
    mock_config_get_bool.return_value = True
    event_extraction_cli.main()
    assert not settings.verify_ssl_certs


def test_main_when_config_arg_ignore_ssl_errors_is_false_py42_settings_verify_ssl_certs_is_true(
    mock_42,
    mock_arg_parse,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_bool,
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
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_bool,
):
    mock_config_get_bool.return_value = True
    event_extraction_cli.main()
    assert settings.debug_level == debug_level.DEBUG


def test_main_when_config_arg_debug_mode_is_false_that_py42_settings_debug_mode_is_not_debug(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_bool,
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
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_arg,
):
    mock_config_get_arg.return_value = "1970-10-31"
    with pytest.raises(SystemExit):
        event_extraction_cli.main()


def test_main_when_cli_arg_begin_date_is_not_given_uses_min_timestamp_from_sixty_days_ago(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    event_extraction_cli.main()
    expected = (
        (datetime.now() - timedelta(days=60)) - datetime.utcfromtimestamp(0)
    ).total_seconds()
    actual = mock_aed_extractor.call_args[0][0]
    assert pytest.approx(expected, actual)


def test_main_when_cli_arg_end_date_is_not_given_uses_max_timestamp_from_now(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    event_extraction_cli.main()
    expected = (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()
    actual = mock_aed_extractor.call_args[0][1]
    assert pytest.approx(expected, actual)


def test_main_when_destination_is_not_none_and_destination_type_is_stdout_exits(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_destination_type = "stdout"
    mock_args.c42_destination = "Delaware"
    with pytest.raises(SystemExit):
        event_extraction_cli.main()


def test_main_when_destination_is_none_and_destination_type_is_syslog_exits(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_destination_type = "syslog"
    mock_args.c42_destination = None
    with pytest.raises(SystemExit):
        event_extraction_cli.main()


def test_main_when_destination_is_none_and_destination_type_is_file_exits(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_destination_type = "file"
    mock_args.c42_destination = None



def test_main_creates_sdk_with_cli_args_and_stored_password(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"
    mock_args.c42_authority_url = expected_authority
    mock_args.c42_username = expected_username
    mock_get_password.return_value = expected_password
    event_extraction_cli.main()
    mock_42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_creates_sdk_with_config_args_and_stored_password(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_arg,
):
    mock_args.c42_authority_url = None
    mock_args.c42_username = None

    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"
    mock_get_password.return_value = expected_password

    def get_config_arg_side_effect(key):
        if key == "server":
            return expected_authority
        if key == "username":
            return expected_username

    mock_config_get_arg.side_effect = get_config_arg_side_effect
    event_extraction_cli.main()
    mock_42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_creates_sdk_favoring_cli_args_over_config_args(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_arg,
):
    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"
    mock_args.c42_authority_url = expected_authority
    mock_args.c42_username = expected_username
    mock_get_password.return_value = expected_password

    def get_config_arg_side_effect(key):
        # This value should not be used because cli args are favored and set above.
        bad_str = "https://FreeViruses.example.net"
        if key == "server" or key == "username":
            return bad_str

    mock_config_get_arg.side_effect = get_config_arg_side_effect

    event_extraction_cli.main()
    mock_42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_when_get_password_returns_none_uses_password_from_getpass(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_getpass,
):
    mock_get_password.return_value = None
    expected = "super_secret_password"
    mock_getpass.return_value = expected
    event_extraction_cli.main()
    actual = mock_42.call_args[1]["password"]
    assert actual == expected


def test_main_when_get_password_returns_none_calls_set_password_with_password_from_getpass(
    mocker,
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_getpass,
):
    expected_username = "ME"
    expected_password = "super_secret_password"
    mock_args.c42_username = expected_username
    mock_get_password.return_value = None
    mock_getpass.return_value = expected_password
    mock_set_password = mocker.patch("c42seceventcli.aed.event_extraction_cli.set_password")
    event_extraction_cli.main()
    mock_set_password.assert_called_once_with(
        u"c42seceventcli", expected_username, expected_password
    )


def test_main_when_output_format_not_supports_exits(
    mock_42, mock_arg_parse, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    mock_args.c42_output_format = "EAS3"
    with pytest.raises(SystemExit):
        event_extraction_cli.main()


def test_main_when_cli_arg_output_format_is_json_creates_json_formatter(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_get_logger,
):
    mock_args.c42_output_format = "JSON"
    event_extraction_cli.main()
    expected = AEDDictToJSONFormatter
    actual = type(mock_get_logger.call_args[0][0])
    assert actual == expected


def test_main_when_config_arg_output_format_is_json_creates_json_formatter(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_arg,
    mock_get_logger,
):
    def get_config_arg_side_effect(key):
        if key == "output_format":
            return "JSON"

    mock_config_get_arg.side_effect = get_config_arg_side_effect
    event_extraction_cli.main()
    expected = AEDDictToJSONFormatter
    actual = type(mock_get_logger.call_args[0][0])
    assert actual == expected


def test_main_when_cli_arg_output_format_is_cef_creates_cef_formatter(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_get_logger,
):
    mock_args.c42_output_format = "CEF"
    event_extraction_cli.main()
    expected = AEDDictToCEFFormatter
    actual = type(mock_get_logger.call_args[0][0])
    assert actual == expected


def test_main_when_config_arg_output_format_is_cer_creates_cef_formatter(
    mock_42,
    mock_arg_parse,
    mock_args,
    mock_aed_extractor,
    mock_config_parser,
    mock_get_password,
    mock_config_get_arg,
    mock_get_logger,
):
    def get_config_arg_side_effect(key):
        if key == "output_format":
            return "CEF"

    mock_config_get_arg.side_effect = get_config_arg_side_effect
    event_extraction_cli.main()
    expected = AEDDictToCEFFormatter
    actual = type(mock_get_logger.call_args[0][0])
    assert actual == expected
