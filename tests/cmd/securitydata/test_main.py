import pytest

import code42cli.cmd.securitydata.main as main


@pytest.fixture
def mock_logger_factory(mocker):
    return mocker.patch("code42cli.cmd.securitydata.main.logger_factory")


@pytest.fixture
def mock_extract(mocker):
    return mocker.patch("code42cli.cmd.securitydata.main.extract")


def test_print_out(sdk, profile, namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_stdout.return_value = logger
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
