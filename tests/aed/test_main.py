import pytest
from datetime import datetime, timedelta
from socket import gaierror

from py42 import settings
import py42.debug_level as debug_level
from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter
from c42seceventcli.aed.cursor_store import AEDCursorStore
from c42seceventcli.aed.args import AEDArgs

from c42seceventcli.aed import main


@pytest.fixture
def patches(
    mocker,
    mock_aed_extractor_constructor,
    mock_aed_extractor,
    mock_store,
    mock_42,
    mock_args,
    mock_args_getter,
    mock_password_getter,
    mock_password_deleter,
    mock_logger,
    mock_error_logger,
    mock_cursor_reset_function,
):
    mock = mocker.MagicMock()
    mock.aed_extractor_constructor = mock_aed_extractor_constructor
    mock.aed_extractor = mock_aed_extractor
    mock.store = mock_store
    mock.py42 = mock_42
    mock.aed_args = mock_args
    mock.args_getter = mock_args_getter
    mock.get_password = mock_password_getter
    mock.delete_password = mock_password_deleter
    mock.get_logger = mock_logger
    mock.error_logger = mock_error_logger
    mock.reset_cursor = mock_cursor_reset_function
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
def mock_args(mocker, mock_args_getter):
    args = AEDArgs()
    args.cli_parser = mocker.MagicMock()
    args.c42_authority_url = "https://example.com"
    args.c42_username = "test.testerson@example.com"
    mock_args_getter.return_value = args
    return args


@pytest.fixture
def mock_args_getter(mocker):
    return mocker.patch("c42seceventcli.aed.args.get_args")


@pytest.fixture
def mock_password_getter(mocker):
    mock = mocker.patch("c42seceventcli.common.util.get_stored_password")
    mock.get_password.return_value = "PASSWORD"
    return mock


@pytest.fixture
def mock_password_deleter(mocker):
    return mocker.patch("c42seceventcli.common.util.delete_stored_password")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("c42seceventcli.common.util.get_logger")


@pytest.fixture
def mock_error_logger(mocker):
    return mocker.patch("c42seceventcli.common.util.get_error_logger")


@pytest.fixture
def mock_cursor_reset_function(mocker):
    return mocker.patch("c42seceventcli.aed.main.AEDCursorStore.reset")


def test_main_when_get_args_raises_value_error_causes_system_exit(patches):
    patches.args_getter.side_effect = ValueError
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_ignore_ssl_errors_is_true_that_py42_settings_verify_ssl_certs_is_false(patches):
    patches.aed_args.ignore_ssl_errors = True
    main.main()
    assert not settings.verify_ssl_certs


def test_main_when_ignore_ssl_errors_is_false_that_py42_settings_verify_ssl_certs_is_true(patches):
    patches.args.ignore_ssl_errors = False
    main.main()
    assert settings.verify_ssl_certs


def test_main_when_reset_password_is_true_calls_delete_password(patches):
    expected_username = "Bob"
    patches.aed_args.c42_username = expected_username
    patches.aed_args.reset_password = True
    main.main()
    patches.delete_password.assert_called_once_with(main._SERVICE_NAME, expected_username)


def test_main_when_reset_password_is_false_does_not_call_delete_password(patches):
    patches.aed_args.reset_password = False
    main.main()
    assert not patches.delete_password.call_count


def test_main_when_clear_cursor_is_true_calls_aed_cursor_store_reset(patches):
    patches.aed_args.record_cursor = True
    patches.aed_args.clear_cursor = True
    main.main()
    assert patches.reset_cursor.call_count == 1


def test_main_when_clear_cursor_is_false_does_not_call_aed_cursor_store_reset(patches):
    patches.aed_args.record_cursor = True
    patches.aed_args.clear_cursor = False
    main.main()
    assert not patches.reset_cursor.call_count


def test_main_when_debug_mode_is_true_that_py42_settings_debug_mode_is_debug(patches):
    patches.aed_args.debug_mode = True
    main.main()
    assert settings.debug_level == debug_level.DEBUG


def test_main_uses_min_timestamp_from_sixty_days_ago(patches):
    main.main()
    expected = (
        (datetime.now() - timedelta(days=60)) - datetime.utcfromtimestamp(0)
    ).total_seconds()
    actual = patches.aed_extractor.call_args[0][0]
    assert pytest.approx(expected, actual)


def test_main_uses_max_timestamp_from_now(patches):
    main.main()
    expected = (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()
    actual = patches.aed_extractor.call_args[0][1]
    assert pytest.approx(expected, actual)


def test_main_when_create_sdk_raises_exception_causes_exit(patches):
    patches.py42.side_effect = Exception
    with pytest.raises(SystemExit):
        main.main()


def test_main_creates_sdk_with_args_and_password_from_get_password(patches):
    expected_authority = "https://user.authority.com"
    expected_username = "user.userson@userson.solutions"
    expected_password = "querty"
    patches.aed_args.c42_authority_url = expected_authority
    patches.aed_args.c42_username = expected_username
    patches.get_password.return_value = expected_password
    main.main()
    patches.py42.assert_called_once_with(
        host_address=expected_authority, username=expected_username, password=expected_password
    )


def test_main_when_output_format_not_supported_causes_exit(patches):
    patches.aed_args.output_format = "EAS3"
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_output_format_is_json_creates_json_formatter(patches):
    patches.aed_args.output_format = "JSON"
    main.main()
    expected = AEDDictToJSONFormatter
    actual = type(patches.get_logger.call_args[1]["formatter"])
    assert actual == expected


def test_main_when_output_format_is_cef_creates_cef_formatter(patches):
    patches.aed_args.output_format = "CEF"
    main.main()
    expected = AEDDictToCEFFormatter
    actual = type(patches.get_logger.call_args[1]["formatter"])
    assert actual == expected


def test_main_when_destination_port_is_set_passes_port_to_get_logger(patches):
    expected = 1000
    patches.aed_args.destination_port = expected
    main.main()
    actual = patches.get_logger.call_args[1]["destination_port"]
    assert actual == expected


def test_main_when_given_destination_protocol_via_cli_passes_port_to_get_logger(patches):
    expected = "SOME PROTOCOL"
    patches.aed_args.destination_protocol = expected
    main.main()
    actual = patches.get_logger.call_args[1]["destination_protocol"]
    assert actual == expected


def test_main_when_get_logger_raises_io_error_causes_exit(patches):
    patches.get_logger.side_effect = IOError
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_get_logger_raises_gaierror_causes_exit(patches):
    patches.get_logger.side_effect = gaierror
    with pytest.raises(SystemExit):
        main.main()


def test_main_when_record_cursor_is_true_overrides_handlers_record_cursor_position(mocker, patches):
    expected = mocker.MagicMock()
    AEDCursorStore.replace_stored_insertion_timestamp = expected
    patches.aed_args.record_cursor = True
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].record_cursor_position
    assert actual is expected


def test_main_when_record_cursor_is_false_does_not_override_handlers_record_cursor_position(
    mocker, patches
):
    unexpected = mocker.MagicMock()
    AEDCursorStore.replace_stored_insertion_timestamp = unexpected
    patches.aed_args.record_cursor = False
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].record_cursor_position
    assert actual is not unexpected


def test_main_when_record_cursor_is_true_overrides_handlers_get_cursor_position(mocker, patches):
    expected = mocker.MagicMock()
    AEDCursorStore.get_stored_insertion_timestamp = expected
    patches.aed_args.record_cursor = True
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].get_cursor_position
    assert actual is expected


def test_main_when_record_cursor_is_false_does_not_override_handlers_get_cursor_position(
    mocker, patches
):
    unexpected = mocker.MagicMock()
    AEDCursorStore.get_stored_insertion_timestamp = unexpected
    patches.aed_args.record_cursor = False
    main.main()
    actual = patches.aed_extractor_constructor.call_args[0][1].get_cursor_position
    assert actual is not unexpected
