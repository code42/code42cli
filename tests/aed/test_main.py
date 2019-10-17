import pytest
from argparse import Namespace
from datetime import datetime, timedelta

from py42 import settings
import py42.debug_level as debug_level
from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter
from c42seceventcli.aed.cursor_store import AEDCursorStore

from c42seceventcli.aed import main


@pytest.fixture
def patches(
    mocker,
    mock_aed_extractor_constructor,
    mock_aed_extractor,
    mock_store,
    mock_42,
    mock_cli_arg_parser,
    mock_cli_args,
    mock_config_arg_parser,
    mock_config_args,
    mock_get_password_function,
    mock_logger,
    mock_getpass_function,
):
    mock = mocker.MagicMock()
    mock.aed_extractor_constructor = mock_aed_extractor_constructor
    mock.aed_extractor = mock_aed_extractor
    mock.store = mock_store
    mock.py42 = mock_42
    mock.cli_arg_parser = mock_cli_arg_parser
    mock.cli_args = mock_cli_args
    mock.config_arg_parser = mock_config_arg_parser
    mock.config_args = mock_config_args
    mock.get_password = mock_get_password_function
    mock.logger = mock_logger
    mock.getpass = mock_getpass_function
    return mock


@pytest.fixture
def mock_aed_extractor_constructor(mocker):
    mock = mocker.patch("c42secevents.extractors.AEDEventExtractor.__init__")
    mock.return_value = None
    return mock


@pytest.fixture
def mock_aed_extractor(mocker):
    return mocker.patch("c42secevents.extractors.AEDEventExtractor.extract")


@pytest.fixture
def mock_store(mocker):
    store = mocker.patch("c42seceventcli.aed.main.AEDCursorStore.__init__")
    store.return_value = None
    return store


@pytest.fixture
def mock_42(mocker):
    settings.verify_ssl_certs = True
    settings.debug_level = debug_level.NONE
    return mocker.patch("py42.sdk.SDK.create_using_local_account")


@pytest.fixture
def mock_cli_arg_parser(mocker, mock_cli_args):
    mock_parser = mocker.patch("argparse.ArgumentParser.parse_args")
    mock_parser.return_value = mock_cli_args
    return mock_parser


@pytest.fixture
def mock_cli_args():
    args = Namespace()
    args.c42_config_file = None
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
def mock_config_arg_parser(mocker, mock_config_args):
    mock_parser = mocker.patch("c42seceventcli.aed.main.get_config_args")
    mock_parser.return_value = mock_config_args
    return mock_parser


@pytest.fixture
def mock_config_args():
    return {
        "c42_authority_url": None,
        "c42_username": None,
        "c42_begin_date": None,
        "c42_end_date": None,
        "c42_ignore_ssl_errors": None,
        "c42_output_format": None,
        "c42_record_cursor": None,
        "c42_exposure_types": None,
        "c42_debug_mode": None,
        "c42_destination_type": None,
        "c42_destination": None,
        "c42_syslog_port": None,
        "c42_syslog_protocol": None,
    }


@pytest.fixture
def mock_get_password_function(mocker):
    mock = mocker.patch("c42seceventcli.aed.main.get_password")
    mock.get_password.return_value = "PASSWORD"
    return mock


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("c42seceventcli.aed.main.get_logger")


@pytest.fixture
def mock_getpass_function(mocker):
    return mocker.patch("c42seceventcli.aed.main.getpass")


def test_main_when_cli_arg_ignore_ssl_errors_is_true_that_py42_settings_verify_ssl_certs_is_false(patches):
    patches.cli_args.c42_ignore_ssl_errors = True
    main.main()
    assert not settings.verify_ssl_certs


def test_main_when_cli_arg_ignore_ssl_errors_is_false_that_py42_settings_verify_ssl_certs_is_true(patches):
    patches.cli_args.c42_ignore_ssl_errors = False
    main.main()
    assert settings.verify_ssl_certs


def test_main_when_config_arg_ignore_ssl_errors_is_true_py42_settings_verify_ssl_certs_is_false(patches):
    patches.config_args["c42_ignore_ssl_errors"] = True
    main.main()
    assert not settings.verify_ssl_certs


def test_main_when_config_arg_ignore_ssl_errors_is_false_py42_settings_verify_ssl_certs_is_true(patches):
    patches.config_args["c42_ignore_ssl_errors"] = False
    main.main()
    assert settings.verify_ssl_certs


def test_main_when_cli_arg_debug_mode_is_true_that_py42_settings_debug_mode_is_debug(patches):
    patches.cli_args.c42_debug_mode = True
    main.main()
    assert settings.debug_level == debug_level.DEBUG


def test_main_when_config_arg_debug_mode_is_true_that_py42_settings_debug_mode_is_debug(patches):
    patches.config_args["c42_debug_mode"] = True
    main.main()
    assert settings.debug_level == debug_level.DEBUG


def test_main_when_cli_arg_begin_date_is_before_ninety_days_causes_program_exit(patches):
    patches.cli_args.c42_begin_date = "1970-10-31"
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_config_arg_begin_date_is_before_ninety_days_causes_program_exit(patches):
    patches.config_args["c42_begin_date"] = "1970-10-31"
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_cli_arg_begin_date_is_not_given_uses_min_timestamp_from_sixty_days_ago(patches):
    main.main()
    expected = (
        (datetime.now() - timedelta(days=60)) - datetime.utcfromtimestamp(0)
    ).total_seconds()
    actual = patches.aed_extractor.call_args[0][0]
    assert pytest.approx(expected, actual)


def test_main_when_cli_arg_end_date_is_not_given_uses_max_timestamp_from_now(patches):
    main.main()
    expected = (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()
    actual = patches.aed_extractor.call_args[0][1]
    assert pytest.approx(expected, actual)


def test_main_when_destination_is_not_none_and_destination_type_is_stdout_causes_exit(patches):
    patches.cli_args.c42_destination_type = "stdout"
    patches.cli_args.c42_destination = "Delaware"
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_destination_is_none_and_destination_type_is_syslog_causes_exit(patches):
    patches.cli_args.c42_destination_type = "syslog"
    patches.cli_args.c42_destination = None
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_destination_is_none_and_destination_type_is_file_causes_exit(patches):
    patches.cli_args.c42_destination_type = "file"
    patches.cli_args.c42_destination = None
    with pytest.raises(SystemExit):
        main.main()


def test_main_creates_sdk_with_cli_args_and_stored_password(patches):
    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"
    patches.cli_args.c42_authority_url = expected_authority
    patches.cli_args.c42_username = expected_username
    patches.get_password.return_value = expected_password
    main.main()
    patches.py42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_creates_sdk_with_config_args_and_stored_password(patches):
    patches.cli_args.c42_authority_url = None
    patches.cli_args.c42_username = None

    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"

    patches.config_args["c42_authority_url"] = expected_authority
    patches.config_args["c42_username"] = expected_username

    patches.get_password.return_value = expected_password
    main.main()
    patches.py42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_creates_sdk_favoring_cli_args_over_config_args(patches):
    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"
    patches.cli_args.c42_authority_url = expected_authority
    patches.cli_args.c42_username = expected_username

    patches.config_args["c42_authority_url"] = "DO NOT USE"
    patches.config_args["c42_username"] = "NOT REAL PERSON"

    patches.get_password.return_value = expected_password
    main.main()
    patches.py42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_when_get_password_returns_none_uses_password_from_getpass(patches):
    patches.get_password.return_value = None
    expected = "super_secret_password"
    patches.getpass.return_value = expected
    main.main()
    actual = patches.py42.call_args[1]["password"]
    assert actual == expected


def test_main_when_get_password_returns_none_calls_set_password_with_password_from_getpass(mocker, patches):
    expected_username = "ME"
    expected_password = "super_secret_password"
    patches.cli_args.c42_username = expected_username
    patches.get_password.return_value = None
    patches.getpass.return_value = expected_password
    mock_set_password = mocker.patch("c42seceventcli.aed.main.set_password")
    main.main()
    mock_set_password.assert_called_once_with(
        u"c42seceventcli", expected_username, expected_password
    )


def test_main_when_output_format_not_supported_exits(patches):
    patches.cli_args.c42_output_format = "EAS3"
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_cli_arg_output_format_is_json_creates_json_formatter(patches):
    patches.cli_args.c42_output_format = "JSON"
    main.main()
    expected = AEDDictToJSONFormatter
    actual = type(patches.logger.call_args[1]["formatter"])
    assert actual == expected


def test_main_when_config_arg_output_format_is_json_creates_json_formatter(patches):
    patches.config_args["c42_output_format"] = "JSON"
    main.main()
    expected = AEDDictToJSONFormatter
    actual = type(patches.logger.call_args[1]["formatter"])
    assert actual == expected


def test_main_when_cli_arg_output_format_is_cef_creates_cef_formatter(patches):
    patches.cli_args.c42_output_format = "CEF"
    main.main()
    expected = AEDDictToCEFFormatter
    actual = type(patches.logger.call_args[1]["formatter"])
    assert actual == expected


def test_main_when_config_arg_output_format_is_cef_creates_cef_formatter(patches):
    patches.config_args["c42_output_format"] = "CEF"
    main.main()
    expected = AEDDictToCEFFormatter
    actual = type(patches.logger.call_args[1]["formatter"])
    assert actual == expected


def test_main_when_given_syslog_port_via_cli_passes_port_to_get_logger(patches):
    expected = 1000
    patches.cli_args.c42_syslog_port = expected
    main.main()
    actual = patches.logger.call_args[1]["syslog_port"]
    assert actual == expected


def test_main_when_given_syslog_port_via_config_file_passes_port_to_get_logger(patches):
    expected = 1000
    patches.config_args["c42_syslog_port"] = expected
    patches.cli_args.c42_syslog_port = expected
    main.main()
    actual = patches.logger.call_args[1]["syslog_port"]
    assert actual == expected


def test_main_when_given_syslog_protocol_via_cli_passes_port_to_get_logger(patches):
    expected = "SOME PROTOCOL"
    patches.cli_args.c42_syslog_protocol = expected
    main.main()
    actual = patches.logger.call_args[1]["syslog_protocol"]
    assert actual == expected


def test_main_when_given_syslog_protocol_via_config_file_passes_port_to_get_logger(patches):
    expected = "SOME PROTOCOL"
    patches.config_args["c42_syslog_protocol"] = expected
    main.main()
    actual = patches.logger.call_args[1]["syslog_protocol"]
    assert actual == expected


def test_main_when_cli_record_cursor_arg_is_true_overrides_handlers_record_cursor_position(mocker, patches):
    expected = mocker.MagicMock()
    AEDCursorStore.replace_stored_insertion_timestamp = expected
    patches.cli_args.c42_record_cursor = True
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].record_cursor_position
    assert actual is expected


def test_main_when_cli_record_cursor_arg_is_false_does_not_override_handlers_record_cursor_position(mocker, patches):
    unexpected = mocker.MagicMock()
    AEDCursorStore.replace_stored_insertion_timestamp = unexpected
    patches.cli_args.c42_record_cursor = False
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].record_cursor_position
    assert actual is not unexpected


def test_main_when_cli_record_cursor_arg_is_true_overrides_handlers_get_cursor_position(mocker, patches):
    expected = mocker.MagicMock()
    AEDCursorStore.get_stored_insertion_timestamp = expected
    patches.cli_args.c42_record_cursor = True
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].get_cursor_position
    assert actual is expected


def test_main_when_cli_record_cursor_arg_is_false_does_not_override_handlers_get_cursor_position(mocker, patches):
    unexpected = mocker.MagicMock()
    AEDCursorStore.get_stored_insertion_timestamp = unexpected
    patches.cli_args.c42_record_cursor = False
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].get_cursor_position
    assert actual is not unexpected


def test_main_when_config_record_cursor_arg_is_true_overrides_handlers_record_cursor_position(mocker, patches):
    expected = mocker.MagicMock()
    AEDCursorStore.replace_stored_insertion_timestamp = expected
    patches.config_args["c42_record_cursor"] = True
    main.main()
    record_method = patches.aed_extractor_constructor.call_args[0][1].record_cursor_position
    assert record_method is expected


def test_main_when_config_record_cursor_arg_is_false_does_not_override_handlers_record_cursor_position(mocker,patches):
    unexpected = mocker.MagicMock()
    AEDCursorStore.replace_stored_insertion_timestamp = unexpected
    patches.config_args["c42_record_cursor"] = False
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].record_cursor_position
    assert actual is not unexpected


def test_main_when_config_record_cursor_arg_is_true_overrides_handlers_get_cursor_position(mocker, patches):
    expected = mocker.MagicMock()
    AEDCursorStore.get_stored_insertion_timestamp = expected
    patches.config_args["c42_record_cursor"] = True
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].get_cursor_position
    assert actual is expected


def test_main_when_config_record_cursor_arg_is_false_does_not_override_handlers_get_cursor_position(mocker, patches):
    unexpected = mocker.MagicMock()
    AEDCursorStore.get_stored_insertion_timestamp = unexpected
    patches.config_args["c42_record_cursor"] = False
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].get_cursor_position
    assert actual is not unexpected
