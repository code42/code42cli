import pytest
from argparse import ArgumentParser

from .conftest import get_subcommands_root_path
import code42cli.securitydata.subcommands.print_out as printer


def get_patch_path():
    return "{0}.print_out".format(get_subcommands_root_path())


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("{0}.get_logger_for_stdout".format(get_patch_path()))


@pytest.fixture
def extractor(mocker):
    return mocker.patch("{0}.extract".format(get_patch_path()))


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
