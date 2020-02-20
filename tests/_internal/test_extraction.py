import pytest
from argparse import Namespace

from c42sec._internal.extraction import extract


@pytest.fixture
def mock_42(mocker):
    mock = mocker.patch("py42.sdk.SDK.create_using_local_account")
    return mock


@pytest.fixture
def mock_logger(mocker):
    mock = mocker.MagicMock()
    mock.info = mocker.MagicMock()
    return mock


@pytest.fixture
def mock_error_logger(mocker):
    return mocker.patch("c42sec._internal.logger_factory")


@pytest.fixture
def mock_store(mocker):
    mock = mocker.patch("c42secevents.extractors.AEDCursorStore.__init__")
    mock.return_value = None
    return mock


@pytest.fixture
def mock_extractor(mocker):
    mock = mocker.MagicMock()
    mock.extract_raw = mocker.patch("c42secevents.extractors.AEDEventExtractor.extract_raw")
    mock.extract = mocker.patch("c42secevents.extractors.AEDEventExtractor.extract")
    return mock


@pytest.fixture
def mock_namespace_args(mocker):
    mock = mocker.MagicMock(spec=Namespace)
    mock.is_incremental = None
    mock.advanced_query = None
    mock.is_debug_mode = None
    mock.begin_date = None
    mock.end_date = None
    mock.exposure_types = None
    return mock


def test_extract_when_is_advanced_query_uses_only_the_extract_raw_method(
    mock_42, mock_logger, mock_error_logger, mock_namespace_args, mock_extractor
):
    mock_namespace_args.advanced_query = "some complex json"
    extract(mock_logger, mock_namespace_args)
    mock_extractor.extract_raw.assert_called_once_with("some complex json")
    assert mock_extractor.extract.call_count == 0



