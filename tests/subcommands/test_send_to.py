import pytest

from c42sec.subcommands.send_to import send_to


@pytest.fixture
def server_namespace(namespace):
    namespace.server = "https://www.syslog.example.com"
    namespace.protocol = "TCP"
    namespace.format = "CEF"
    return namespace


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("c42sec.subcommands.send_to.get_logger_for_server")


@pytest.fixture
def extractor(mocker):
    return mocker.patch("c42sec.subcommands.send_to.extract")


def test_send_to_uses_logger_for_server(server_namespace, logger_factory, extractor):
    send_to(server_namespace)
    logger_factory.assert_called_once_with("https://www.syslog.example.com", "TCP", "CEF")


def test_send_to_calls_extract_with_expected_arguments(
    mocker, server_namespace, logger_factory, extractor
):
    logger = mocker.MagicMock()
    logger_factory.return_value = logger
    send_to(server_namespace)
    extractor.assert_called_once_with(logger, server_namespace)
