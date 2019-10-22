import pytest
from argparse import Namespace

from c42seceventcli.aed.args import get_args


@pytest.fixture
def patches(mocker, mock_cli_arg_parser, mock_cli_args, mock_config_arg_parser, mock_config_args):
    mock = mocker.MagicMock()
    mock.cli_args = mock_cli_args
    mock.config_args = mock_config_args
    return mock


@pytest.fixture
def mock_cli_args():
    args = Namespace()
    args.reset_password = None
    args.clear_cursor = None
    args.config_file = None
    args.c42_authority_url = None
    args.c42_username = None
    args.begin_date = None
    args.end_date = None
    args.ignore_ssl_errors = None
    args.output_format = None
    args.record_cursor = None
    args.exposure_types = None
    args.debug_mode = None
    args.destination_type = None
    args.destination = None
    args.destination_port = None
    args.destination_protocol = None
    return args


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
        "c42_destination_port": None,
        "c42_destination_protocol": None,
    }


@pytest.fixture
def mock_config_arg_parser(mocker, mock_config_args):
    mock_parser = mocker.patch("c42seceventcli.common.common.get_config_args")
    mock_parser.return_value = mock_config_args
    return mock_parser


@pytest.fixture
def mock_cli_arg_parser(mocker, mock_cli_args):
    mock_parser = mocker.patch("argparse.ArgumentParser.parse_args")
    mock_parser.return_value = mock_cli_args
    return mock_parser


def test_get_args_when_cli_authority_url_is_set_returns_args_with_same_username(patches):
    expected_url = "https://www.example.com"
    patches.cli_args.c42_authority_url = expected_url
    args = get_args()
    assert args.c42_authority_url == expected_url


def test_get_args_when_config_authority_url_is_set_returns_args_with_same_username(patches):
    expected_url = "https://www.example.com"
    patches.config_args["c42_authority_url"] = expected_url
    args = get_args()
    assert args.c42_authority_url == expected_url


def test_get_args_favors_cli_authority_url_over_config_authority_url(patches):
    expected_url = "https://www.example.com"
    patches.cli_args.c42_authority_url = expected_url
    patches.config_args["c42_authority_url"] = "https://virus_probably.com"
    args = get_args()
    assert args.c42_authority_url == expected_url


def test_get_args_when_cli_username_is_set_returns_args_with_same_username(patches):
    expected_user = "FirstUser"
    patches.cli_args.c42_username = expected_user
    args = get_args()
    assert args.c42_username == expected_user


def test_get_args_when_config_username_is_set_returns_args_with_same_username(patches):
    expected_user = "FirstUser"
    patches.config_args["c42_username"] = expected_user
    args = get_args()
    assert args.c42_username == expected_user


def test_get_args_favors_cli_username_over_config_username(patches):
    expected_user = "FirstUser"
    patches.cli_args.c42_username = expected_user
    patches.config_args["c42_username"] = "SecondUser"
    args = get_args()
    assert args.c42_username == expected_user


def test_verify_destination_args_when_destination_is_not_none_and_destination_type_is_stdout_causes_exit(
    patches
):
    patches.cli_args.destination_type = "stdout"
    patches.cli_args.destination = "Delaware"
    with pytest.raises(AttributeError):
        get_args()


def test_verify_destination_args_when_destination_is_none_and_destination_type_is_server_causes_exit(
    patches
):
    patches.cli_args.destination_type = "server"
    patches.cli_args.destination = None
    with pytest.raises(AttributeError):
        get_args()


def test_verify_destination_args_when_destination_is_none_and_destination_type_is_file_causes_exit(
    patches
):
    patches.cli_args.destination_type = "file"
    patches.cli_args.destination = None
    with pytest.raises(AttributeError):
        get_args()
