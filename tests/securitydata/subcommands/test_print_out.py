from argparse import ArgumentParser

import pytest

import code42cli.securitydata.subcommands.print_out as printer
from code42cli.profile.config import ConfigAccessor
from .conftest import ACCEPTABLE_ARGS
from ..conftest import SUBCOMMANDS_NAMESPACE

_PRINT_PATH = "{0}.print_out".format(SUBCOMMANDS_NAMESPACE)



@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor)
    factory = mocker.patch("")
    factory.return_value = mock
    return mock


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("{0}.get_logger_for_stdout".format(_PRINT_PATH))


@pytest.fixture
def extractor(mocker):
    return mocker.patch("{0}.extract".format(_PRINT_PATH))


def test_init_adds_parser_that_can_parse_supported_args():
    subcommand_parser = ArgumentParser().add_subparsers()
    printer.init(subcommand_parser)
    print_parser = subcommand_parser.choices.get("print")
    print_parser.parse_args(ACCEPTABLE_ARGS)


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
