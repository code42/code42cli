import pytest
from argparse import ArgumentParser

from tests.securitydata.conftest import _SUBCOMMANDS_PATH
from code42cli.securitydata.subcommands import write_to as writer


_WRITE_PATH = "{0}.write_to".format(_SUBCOMMANDS_PATH)


@pytest.fixture
def file_namespace(namespace):
    namespace.filename = "out.txt"
    namespace.format = "CEF"
    return namespace


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("{0}.get_logger_for_file".format(_WRITE_PATH))


@pytest.fixture
def extractor(mocker):
    return mocker.patch("{0}.extract".format(_WRITE_PATH))


def test_init_adds_parser_that_can_parse_supported_args(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    writer.init(subcommand_parser)
    write_parser = subcommand_parser.choices.get("write-to")
    write_parser.parse_args(
        [
            "out.txt",
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


def test_init_adds_parser_when_not_given_filename_causes_system_exit(config_parser):
    subcommand_parser = ArgumentParser().add_subparsers()
    writer.init(subcommand_parser)
    write_parser = subcommand_parser.choices.get("write-to")
    with pytest.raises(SystemExit):
        write_parser.parse_args(
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


def test_write_to_uses_logger_for_file(file_namespace, logger_factory, extractor):
    writer.write_to(file_namespace)
    logger_factory.assert_called_once_with("out.txt", "CEF")


def test_write_to_calls_extract_with_expected_arguments(
    mocker, file_namespace, logger_factory, extractor
):
    logger = mocker.MagicMock()
    logger_factory.return_value = logger
    writer.write_to(file_namespace)
    extractor.assert_called_once_with(logger, file_namespace)
