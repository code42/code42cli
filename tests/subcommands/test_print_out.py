import pytest

from c42sec.subcommands.print_out import print_out


@pytest.fixture
def logger_factory(mocker):
    return mocker.patch("c42sec.subcommands.print_out.get_logger_for_stdout")


@pytest.fixture
def extractor(mocker):
    return mocker.patch("c42sec.subcommands.print_out.extract")


def test_print_out_uses_logger_for_stdout(namespace, logger_factory, extractor):
    namespace.format = "CEF"
    print_out(namespace)
    logger_factory.assert_called_once_with("CEF")


def test_print_out_calls_extract_with_expected_arguments(
    mocker, namespace, logger_factory, extractor
):
    namespace.format = "CEF"
    logger = mocker.MagicMock()
    logger_factory.return_value = logger
    print_out(namespace)
    extractor.assert_called_once_with(logger, namespace)
