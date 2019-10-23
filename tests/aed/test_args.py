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
    return Namespace()


@pytest.fixture
def mock_config_args():
    return {}


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


def test_get_args_calls_sec_args_try_set_with_expected_args(mocker, patches):
    mock_setter = mocker.patch("c42seceventcli.common.common.SecArgs.try_set")
    key = "c42_authority_url"
    expected_cli_val = "URL1"
    expected_config_val = "URL2"
    patches.cli_args.c42_authority_url = expected_cli_val
    patches.config_args[key] = expected_config_val
    get_args()
    mock_setter.assert_called_once_with(key, expected_cli_val, expected_config_val)


def test_get_args_when_destination_is_not_none_and_destination_type_is_stdout_causes_exit(
    patches
):
    patches.cli_args.destination_type = "stdout"
    patches.cli_args.destination = "Delaware"
    with pytest.raises(AttributeError):
        get_args()


def test_get_args_when_destination_is_none_and_destination_type_is_server_causes_exit(
    patches
):
    patches.cli_args.destination_type = "server"
    patches.cli_args.destination = None
    with pytest.raises(AttributeError):
        get_args()


def test_get_args_when_destination_is_none_and_destination_type_is_file_causes_exit(
    patches
):
    patches.cli_args.destination_type = "file"
    patches.cli_args.destination = None
    with pytest.raises(AttributeError):
        get_args()
