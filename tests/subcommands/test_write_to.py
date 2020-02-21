import pytest

from c42sec.subcommands.write_to import write_to


@pytest.fixture
def file_namespace(namespace):
    namespace.filename = "out.txt"
    namespace.format = "CEF"
    return namespace


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("c42sec.subcommands.write_to.get_logger_for_file")


@pytest.fixture
def extractor(mocker):
    return mocker.patch("c42sec.subcommands.write_to.extract")


def test_write_to_uses_logger_for_file(file_namespace, logger_factory, extractor):
    write_to(file_namespace)
    logger_factory.assert_called_once_with("out.txt", "CEF")


def test_write_to_calls_extract_with_expected_arguments(
    mocker, file_namespace, logger_factory, extractor
):
    logger = mocker.MagicMock()
    logger_factory.return_value = logger
    write_to(file_namespace)
    extractor.assert_called_once_with(logger, file_namespace)
