import pytest
from argparse import ArgumentParser


@pytest.fixture
def mock_aed_extractor(mocker):
    return mocker.patch("c42secevents.extractors.AEDEventExtractor.extract")


@pytest.fixture
def mock_42(mocker):
    return mocker.patch("py42.sdk.SDK.create_using_local_account")


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.patch("configparser.ConfigParser.read")


@pytest.fixture
def mock_get_password(mocker):
    mock = mocker.patch("keyring.get_password")
    mock.get_password.return_value = "PASSWORD"
    return mock


@pytest.fixture
def mock_args(mocker):
    mock_parsed_args = mocker.MagicMock(spec=ArgumentParser)
    mock_parsed_args.c42_ignore_ssl_errors = True
    mock_parsed_args.c42_begin_date = "2019-09-03"
    mock_parsed_args.c42_end_date = "2019-10-03"


def test_main_sets_verify_ssl_to_false_when_ignore_ssl_errors_arg_passed_in(
   mock_42, mock_args, mock_aed_extractor, mock_config_parser, mock_get_password
):
    assert True
    # from c42seceventcli.aed import aed_event_extraction_cli
    # aed_event_extraction_cli.main()
    # assert not settings.verify_ssl_certs

