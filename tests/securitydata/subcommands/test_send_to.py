from argparse import ArgumentParser

import pytest

from code42cli.securitydata.subcommands import send_to as sender
from .conftest import ACCEPTABLE_ARGS
from ..conftest import SUBCOMMANDS_NAMESPACE

_SEND_PATH = "{0}.send_to".format(SUBCOMMANDS_NAMESPACE)


@pytest.fixture
def server_namespace(namespace):
    namespace.server = "www.syslog.example.com"
    namespace.protocol = "TCP"
    namespace.format = "CEF"
    return namespace


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("{0}.get_logger_for_server".format(_SEND_PATH))


@pytest.fixture
def extractor(mocker):
    return mocker.patch("{0}.extract".format(_SEND_PATH))


def test_init_adds_parser_that_can_parse_supported_args(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    sender.init(subcommand_parser)
    send_parser = subcommand_parser.choices.get("send-to")
    args = ["https://www.syslog.com", "-p", "UDP"] + ACCEPTABLE_ARGS
    send_parser.parse_args(args)


def test_init_adds_parser_when_not_given_server_causes_system_exit(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    sender.init(subcommand_parser)
    send_parser = subcommand_parser.choices.get("send-to")
    with pytest.raises(SystemExit):
        send_parser.parse_args(
            [
                "-t",
                "SharedToDomain",
                "ApplicationRead",
                "CloudStorage",
                "RemovableMedia",
                "IsPublic",
                "-f",
                "JSON",
                "-d",
                "-b",
                "600",
                "-e",
                "2020-02-02",
            ]
        )


def test_send_to_uses_logger_for_server(server_namespace, logger_factory, extractor):
    sender.send_to(server_namespace)
    logger_factory.assert_called_once_with("www.syslog.example.com", "TCP", "CEF")


def test_send_to_calls_extract_with_expected_arguments(
    mocker, server_namespace, logger_factory, extractor
):
    logger = mocker.MagicMock()
    logger_factory.return_value = logger
    sender.send_to(server_namespace)
    extractor.assert_called_once_with(logger, server_namespace)
