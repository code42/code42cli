from io import StringIO

import py42.sdk
import py42.settings.debug as debug
import pytest
from py42.exceptions import Py42MFARequiredError
from py42.exceptions import Py42UnauthorizedError
from requests import Response
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from requests.exceptions import RequestException

from .conftest import create_mock_profile
from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.main import cli
from code42cli.options import CLIState
from code42cli.sdk_client import create_sdk


@pytest.fixture
def sdk_logger(mocker):
    return mocker.patch("code42cli.sdk_client.logger")


@pytest.fixture
def mock_sdk_factory(mocker):
    return mocker.patch("py42.sdk.from_local_account")


@pytest.fixture
def mock_profile_with_password():
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    return profile


@pytest.fixture
def requests_exception(mocker):
    mock_response = mocker.MagicMock(spec=Response)
    mock_exception = mocker.MagicMock(spec=RequestException)
    mock_exception.response = mock_response
    return mock_exception


def test_create_sdk_when_profile_has_ssl_errors_disabled_sets_py42_setting_and_prints_warning(
    profile, mocker, capsys
):
    mock_py42 = mocker.patch("code42cli.sdk_client.py42")
    profile.ignore_ssl_errors = "True"
    create_sdk(profile, False)
    output = capsys.readouterr()
    assert not mock_py42.settings.verify_ssl_certs
    assert (
        f"Warning: Profile '{profile.name}' has SSL verification disabled. Adding certificate "
        "verification is strongly advised." in output.err
    )


def test_create_sdk_when_py42_exception_occurs_raises_and_logs_cli_error(
    sdk_logger, mock_sdk_factory, requests_exception, mock_profile_with_password
):

    mock_sdk_factory.side_effect = Py42UnauthorizedError(requests_exception)

    with pytest.raises(Code42CLIError) as err:
        create_sdk(mock_profile_with_password, False)

    assert "Invalid credentials for user" in err.value.message
    assert sdk_logger.log_error.call_count == 1
    assert "Failure in HTTP call" in str(sdk_logger.log_error.call_args[0][0])


def test_create_sdk_when_connection_exception_occurs_raises_and_logs_cli_error(
    sdk_logger, mock_sdk_factory, mock_profile_with_password
):
    mock_sdk_factory.side_effect = ConnectionError("connection message")

    with pytest.raises(LoggedCLIError) as err:
        create_sdk(mock_profile_with_password, False)

    assert "Problem connecting to" in err.value.message
    assert sdk_logger.log_error.call_count == 1
    assert "connection message" in str(sdk_logger.log_error.call_args[0][0])


def test_create_sdk_when_unknown_exception_occurs_raises_and_logs_cli_error(
    sdk_logger, mock_sdk_factory, mock_profile_with_password
):
    mock_sdk_factory.side_effect = Exception("test message")

    with pytest.raises(LoggedCLIError) as err:
        create_sdk(mock_profile_with_password, False)

    assert "Unknown problem validating" in err.value.message
    assert sdk_logger.log_error.call_count == 1
    assert "test message" in str(sdk_logger.log_error.call_args[0][0])


def test_create_sdk_when_told_to_debug_turns_on_debug(
    mock_sdk_factory, mock_profile_with_password
):
    create_sdk(mock_profile_with_password, True)
    assert py42.settings.debug.level == debug.DEBUG


def test_create_sdk_uses_given_credentials(
    mock_sdk_factory, mock_profile_with_password
):
    create_sdk(mock_profile_with_password, False)
    mock_sdk_factory.assert_called_once_with(
        "example.com", "foo", "Test Password", totp=None
    )


def test_create_sdk_connection_when_mfa_required_exception_raised_prompts_for_totp(
    mocker, monkeypatch, mock_sdk_factory, capsys, mock_profile_with_password
):
    monkeypatch.setattr("sys.stdin", StringIO("101010"))
    response = mocker.MagicMock(spec=Response)
    mock_sdk_factory.side_effect = [
        Py42MFARequiredError(HTTPError(response=response)),
        None,
    ]
    create_sdk(mock_profile_with_password, False)
    output = capsys.readouterr()
    assert "Multi-factor authentication required. Enter TOTP:" in output.out


def test_create_sdk_connection_when_mfa_token_invalid_raises_expected_cli_error(
    mocker, mock_sdk_factory, mock_profile_with_password
):
    response = mocker.MagicMock(spec=Response)
    response.text = '{"data":null,"error":[{"primaryErrorKey":"INVALID_TIME_BASED_ONE_TIME_PASSWORD","otherErrors":null}],"warnings":null}'
    mock_sdk_factory.side_effect = Py42UnauthorizedError(HTTPError(response=response))
    with pytest.raises(Code42CLIError) as err:
        create_sdk(mock_profile_with_password, False, totp="1234")
    assert str(err.value) == "Invalid TOTP token for user foo."


def test_totp_option_when_passed_is_passed_to_sdk_initialization(
    mocker, profile, runner
):
    mock_py42 = mocker.patch("code42cli.sdk_client.py42.sdk.from_local_account")
    cli_state = CLIState()
    totp = "1234"
    profile.authority_url = "example.com"
    profile.username = "user"
    profile.get_password.return_value = "password"
    cli_state._profile = profile
    runner.invoke(cli, ["users", "list", "--totp", totp], obj=cli_state)
    mock_py42.assert_called_once_with(
        profile.authority_url, profile.username, "password", totp=totp
    )
