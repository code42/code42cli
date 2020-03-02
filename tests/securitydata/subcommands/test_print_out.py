import pytest
from argparse import ArgumentParser

from tests.securitydata.conftest import SUBCOMMANDS_PATH
import code42cli.securitydata.subcommands.print_out as printer


_PRINT_PATH = "{0}.print_out".format(SUBCOMMANDS_PATH)


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("{0}.get_logger_for_stdout".format(_PRINT_PATH))


@pytest.fixture
def extractor(mocker):
    return mocker.patch("{0}.extract".format(_PRINT_PATH))


def test_init_adds_parser_that_can_parse_supported_args(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    printer.init(subcommand_parser)
    print_parser = subcommand_parser.choices.get("print")
    print_parser.parse_args(
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
            "--c42username",
            "test.testerson",
            "--actor",
            "test.testerson",
            "--md5",
            "098f6bcd4621d373cade4e832627b4f6",
            "--sha256",
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            "--source",
            "Gmail",
            "--filename",
            "file.txt",
            "--filepath",
            "/path/to/file.txt",
            "--processOwner",
            "test.testerson",
            "--tabURL",
            "https://example.com"
        ]
    )


def test_print_out_uses_logger_for_stdout(namespace, logger_factory, extractor):
    namespace.format = "CEF"
    printer.print_out(namespace)
    logger_factory.assert_called_once_with("CEF")


def test_print_out_calls_extract_with_expected_arguments(
    mocker, namespace, logger_factory, extractor
):
    namespace.format = "CEF"
    logger = mocker.MagicMock()
    logger_factory.return_value = logger
    printer.print_out(namespace)
    extractor.assert_called_once_with(logger, namespace)
