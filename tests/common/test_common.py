import pytest
from os import path
from datetime import datetime, timedelta
from logging import StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler

from c42secevents.logging.handlers import NoPrioritySysLogHandler

from c42seceventcli.common.common import (
    get_config_args,
    parse_timestamp,
    get_logger,
    get_error_logger,
    SecArgs,
    get_stored_password,
    delete_stored_password,
    get_user_project_path,
)


_DUMMY_KEY = "Key"


@pytest.fixture
def mock_config_read(mocker):
    return mocker.patch("configparser.ConfigParser.read")


@pytest.fixture
def mock_config_get_function(mocker):
    return mocker.patch("configparser.ConfigParser.get")


@pytest.fixture
def mock_config_get_bool_function(mocker):
    return mocker.patch("configparser.ConfigParser.getboolean")


@pytest.fixture
def mock_config_file_reader(mocker):
    reader = mocker.patch("configparser.ConfigParser.read")
    reader.return_value = ["NOT EMPTY LIST"]
    return reader


@pytest.fixture
def mock_config_file_sections(mocker):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = ["NOT EMPTY LIST"]
    return sections


@pytest.fixture
def mock_get_logger(mocker):
    return mocker.patch("logging.getLogger")


@pytest.fixture
def mock_no_priority_syslog_handler(mocker):
    mock_handler_init = mocker.patch(
        "c42secevents.logging.handlers.NoPrioritySysLogHandler.__init__"
    )
    mock_handler_init.return_value = None
    return mock_handler_init


@pytest.fixture
def mock_file_handler(mocker):
    mock_handler_init = mocker.patch("logging.FileHandler.__init__")
    mock_handler_init.return_value = None
    return mock_handler_init


@pytest.fixture
def mock_password_getter(mocker):
    return mocker.patch("keyring.get_password")


@pytest.fixture
def password_patches(
    mocker,
    mock_password_getter,
    mock_password_setter,
    mock_password_deleter,
    mock_get_input,
    mock_getpass_function,
):
    mock = mocker.MagicMock()
    mock.get_password = mock_password_getter
    mock.set_password = mock_password_setter
    mock.delete_password = mock_password_deleter
    mock.getpass = mock_getpass_function
    mock.get_input = mock_get_input
    return mock


@pytest.fixture
def mock_password_setter(mocker):
    return mocker.patch("keyring.set_password")


@pytest.fixture
def mock_password_deleter(mocker):
    return mocker.patch("keyring.delete_password")


@pytest.fixture
def mock_getpass_function(mocker):
    return mocker.patch("getpass.getpass")


@pytest.fixture
def mock_get_input(mocker):
    return mocker.patch("c42seceventcli.common.common._get_input")


@pytest.fixture
def path_patches(mocker, mock_user_expansion, mock_dir_maker, mock_path_existence):
    mock = mocker.MagicMock()
    mock.expand_user = mock_user_expansion
    mock.make_dirs = mock_dir_maker
    mock.path_exists = mock_path_existence
    return mock


@pytest.fixture
def mock_user_expansion(mocker):
    return mocker.patch("os.path.expanduser")


@pytest.fixture
def mock_dir_maker(mocker):
    return mocker.patch("c42seceventcli.common.common.makedirs")


@pytest.fixture
def mock_path_existence(mocker):
    return mocker.patch("os.path.exists")


def test_get_user_project_path_returns_expected_path(path_patches):
    expected_home = "/PATH/"
    expected_subdir = "SUBDIR"
    path_patches.expand_user.return_value = expected_home
    expected = path.join(expected_home, ".c42seceventcli", expected_subdir)
    actual = get_user_project_path(expected_subdir)
    assert actual == expected


def test_get_user_project_path_calls_make_dirs_when_path_does_not_exist(path_patches):
    expected_home = "/PATH/"
    expected_subdir = "SUBDIR"
    path_patches.expand_user.return_value = expected_home
    expected_path = path.join(expected_home, ".c42seceventcli", expected_subdir)
    path_patches.path_exists.return_value = False
    get_user_project_path(expected_subdir)
    path_patches.make_dirs.assert_called_once_with(expected_path)


def test_get_user_project_path_does_not_call_make_dirs_when_path_exists(path_patches):
    expected_home = "/PATH/"
    expected_subdir = "SUBDIR"
    path_patches.expand_user.return_value = expected_home
    path_patches.path_exists.return_value = True
    get_user_project_path(expected_subdir)
    assert not path_patches.make_dirs.call_count


def test_get_config_args_when_read_returns_empty_list_raises_io_error(mocker):
    reader = mocker.patch("configparser.ConfigParser.read")
    reader.return_value = []
    with pytest.raises(IOError):
        get_config_args("Test")


def test_get_config_args_when_sections_returns_empty_list_returns_empty_dict(
    mocker, mock_config_file_reader
):
    sections = mocker.patch("configparser.ConfigParser.sections")
    sections.return_value = []
    assert get_config_args("Test") == {}


def test_get_config_args_returns_dict_made_from_items(
    mocker, mock_config_file_reader, mock_config_file_sections
):
    mock_tuples = mocker.patch("configparser.ConfigParser.items")
    mock_tuples.return_value = [("Hi", "Bye"), ("Pizza", "FrenchFries")]
    arg_dict = get_config_args("Test")
    assert arg_dict == {"Hi": "Bye", "Pizza": "FrenchFries"}


def test_parse_timestamp_when_given_date_format_returns_expected_timestamp():
    date_str = "2019-10-01"
    date = datetime.strptime(date_str, "%Y-%m-%d")
    expected = (date - date.utcfromtimestamp(0)).total_seconds()
    actual = parse_timestamp(date_str)
    assert actual == expected


def test_parse_timestamp_when_given_minutes_ago_format_returns_expected_timestamp():
    minutes_ago = 1000
    now = datetime.utcnow()
    time = now - timedelta(minutes=minutes_ago)
    expected = (time - datetime.utcfromtimestamp(0)).total_seconds()
    actual = parse_timestamp("1000")
    assert pytest.approx(actual, expected)


def test_parse_timestamp_when_given_bad_string_raises_value_error():
    with pytest.raises(ValueError):
        parse_timestamp("BAD!")


def test_get_error_logger_uses_rotating_file_with_expected_args(mocker, mock_get_logger):
    expected_service_name = "TEST_SERVICE"
    mock_handler = mocker.patch("logging.handlers.RotatingFileHandler.__init__")
    mock_handler.return_value = None
    get_error_logger(expected_service_name)
    expected_path = "{0}/{1}_error.log".format(get_user_project_path("log"), expected_service_name)
    mock_handler.assert_called_once_with(expected_path, maxBytes=250000000)


def test_get_logger_when_destination_type_is_stdout_adds_stream_handler_to_logger(mock_get_logger):
    service = "TEST_SERVICE"
    logger = get_logger(None, service, "Somewhere", "stdout")
    actual = type(logger.addHandler.call_args[0][0])
    expected = StreamHandler
    assert actual == expected


def test_get_logger_when_destination_type_is_file_adds_file_handler_to_logger(
    mock_get_logger, mock_file_handler
):
    service = "TEST_SERVICE"
    logger = get_logger(None, service, "Somewhere", "file")
    actual = type(logger.addHandler.call_args[0][0])
    expected = FileHandler
    assert actual == expected


def test_get_logger_when_destination_type_is_server_adds_no_priority_syslog_handler_to_logger(
    mock_get_logger, mock_no_priority_syslog_handler
):
    service = "TEST_SERVICE"
    logger = get_logger(None, service, "Somewhere", "server")
    actual = type(logger.addHandler.call_args[0][0])
    expected = NoPrioritySysLogHandler
    assert actual == expected


def test_get_stored_password_when_keyring_returns_none_uses_password_from_getpass(password_patches):
    password_patches.get_password.return_value = None
    expected = "super_secret_password"
    password_patches.getpass.return_value = expected
    actual = get_stored_password("TEST", "USER")
    assert actual == expected


def test_get_stored_password_returns_same_value_from_keyring(password_patches):
    expected = "super_secret_password"
    password_patches.get_password.return_value = expected
    actual = get_stored_password("TEST", "USER")
    assert actual == expected


def test_get_stored_password_when_keyring_returns_none_and_get_input_returns_y_calls_set_password_with_password_from_getpass(
    password_patches
):
    expected_service_name = "SERVICE"
    expected_username = "ME"
    expected_password = "super_secret_password"
    password_patches.get_password.return_value = None
    password_patches.get_input.return_value = "y"
    password_patches.getpass.return_value = expected_password

    get_stored_password(expected_service_name, expected_username)
    password_patches.set_password.assert_called_once_with(
        expected_service_name, expected_username, expected_password
    )


def test_get_stored_password_when_keyring_returns_none_and_get_input_returns_n_does_not_call_set_password(
    password_patches
):
    expected_service_name = "SERVICE"
    expected_username = "ME"
    expected_password = "super_secret_password"
    password_patches.get_password.return_value = expected_username
    password_patches.get_input.return_value = "n"
    password_patches.getpass.return_value = expected_password

    get_stored_password(expected_service_name, expected_username)
    assert not password_patches.set_password.call_count


def test_delete_stored_password_calls_keyring_delete_password(password_patches):
    expected_service_name = "SERVICE"
    expected_username = "ME"
    delete_stored_password(expected_service_name, expected_username)
    password_patches.delete_password.assert_called_once_with(
        expected_service_name, expected_username
    )


def test_subclass_of_sec_args_try_set_favors_cli_arg_over_config_arg():
    class SubclassSecArgs(SecArgs):
        test = None

    arg_name = "test"
    cli_arg_value = 1
    config_arg_value = 2
    args = SubclassSecArgs()
    args.try_set(arg_name, cli_arg_value, config_arg_value)
    expected = cli_arg_value
    assert args.test == expected
