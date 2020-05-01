import pytest

import code42cli.cmds.securitydata.main as main
from code42cli import PRODUCT_NAME


@pytest.fixture
def mock_logger_factory(mocker):
    return mocker.patch("{}.cmds.securitydata.main.logger_factory".format(PRODUCT_NAME))


@pytest.fixture
def mock_extract(mocker):
    return mocker.patch("{}.cmds.securitydata.main.extract".format(PRODUCT_NAME))


def test_print_out(sdk, profile, namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_stream_logger.return_value = logger
    main.print_out(sdk, profile, namespace)
    mock_extract.assert_called_with(sdk, profile, logger, namespace)


def test_write_to(sdk, profile, namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_file.return_value = logger
    main.write_to(sdk, profile, namespace)
    mock_extract.assert_called_with(sdk, profile, logger, namespace)


def test_send_to(sdk, profile, namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_server.return_value = logger
    main.send_to(sdk, profile, namespace)
    mock_extract.assert_called_with(sdk, profile, logger, namespace)
