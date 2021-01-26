import pytest

from code42cli.cmds.search import try_get_logger_for_server
from code42cli.errors import Code42CLIError
from code42cli.logger.enums import ServerProtocol
from code42cli.output_formats import SendToFileEventsOutputFormat


_TEST_ERROR_MESSAGE = "TEST ERROR MESSAGE"
_TEST_HOST = "example.com"
_TEST_CERTS = "./certs.pem"


@pytest.fixture
def patched_get_logger_method(mocker):
    return mocker.patch("code42cli.cmds.search.get_logger_for_server")


@pytest.fixture
def errored_logger(patched_get_logger_method):
    patched_get_logger_method.side_effect = Exception(_TEST_ERROR_MESSAGE)


def test_try_get_logger_for_server_calls_get_logger_for_server(
    patched_get_logger_method,
):
    try_get_logger_for_server(
        _TEST_HOST,
        ServerProtocol.TLS_TCP,
        SendToFileEventsOutputFormat.CEF,
        _TEST_CERTS,
    )
    patched_get_logger_method.assert_called_once_with(
        _TEST_HOST,
        ServerProtocol.TLS_TCP,
        SendToFileEventsOutputFormat.CEF,
        _TEST_CERTS,
    )


def test_try_get_logger_for_server_when_exception_raised_raises_code42_cli_error(
    errored_logger,
):
    with pytest.raises(Code42CLIError) as err:
        try_get_logger_for_server(
            _TEST_HOST,
            ServerProtocol.TCP,
            SendToFileEventsOutputFormat.RAW,
            _TEST_CERTS,
        )

    assert (
        str(err.value)
        == f"Unable to connect to example.com. Failed with error: {_TEST_ERROR_MESSAGE}."
    )
