import pytest

import code42cli.cmds.securitydata.main as main
from code42cli import PRODUCT_NAME
from code42cli.cmds.search_shared.enums import ExposureType as ExposureTypeOptions


@pytest.fixture
def mock_logger_factory(mocker):
    return mocker.patch("{}.cmds.securitydata.main.logger_factory".format(PRODUCT_NAME))


@pytest.fixture
def mock_extract(mocker):
    return mocker.patch("{}.cmds.securitydata.main.extract".format(PRODUCT_NAME))


def test_print_out(sdk, profile, file_event_namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_stdout.return_value = logger
    main.print_out(sdk, profile, file_event_namespace)
    mock_extract.assert_called_with(sdk, profile, logger, file_event_namespace, None)


def test_write_to(sdk, profile, file_event_namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_file.return_value = logger
    main.write_to(sdk, profile, file_event_namespace)
    mock_extract.assert_called_with(sdk, profile, logger, file_event_namespace, None)


def test_send_to(sdk, profile, file_event_namespace, mocker, mock_logger_factory, mock_extract):
    logger = mocker.MagicMock()
    mock_logger_factory.get_logger_for_server.return_value = logger
    main.send_to(sdk, profile, file_event_namespace)
    mock_extract.assert_called_with(sdk, profile, logger, file_event_namespace, None)


def test_validation_when_is_advanced_query_and_has_begin_date_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.begin = "begin date"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_advanced_query_and_has_end_date_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.end = "end date"
    with pytest.raises(SystemExit):
        main.write_to(sdk, profile, file_event_namespace)


def test_validation_when_is_advanced_query_and_has_exposure_types_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.type = [ExposureTypeOptions.SHARED_TO_DOMAIN]
    with pytest.raises(SystemExit):
        main.send_to(sdk, profile, file_event_namespace)


@pytest.mark.parametrize(
    "arg",
    [
        "c42_username",
        "actor",
        "md5",
        "sha256",
        "source",
        "file_name",
        "file_path",
        "process_owner",
        "tab_url",
    ],
)
def test_validation_when_is_advanced_query_and_other_incompatible_multi_narg_argument_passed(
    sdk, profile, file_event_namespace, arg
):
    file_event_namespace.advanced_query = "some complex json"
    setattr(file_event_namespace, arg, ["test_value"])
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_advanced_query_and_uses_checkpoint_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.use_checkpoint = "foo"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_advanced_query_and_has_include_non_exposure_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.include_non_exposure = True
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_advanced_query_and_has_saved_search_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.advanced_query = "some complex json"
    file_event_namespace.saved_search = "abc"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_saved_search_and_has_begin_date_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.saved_search = "abc"
    file_event_namespace.begin = "begin date"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_saved_search_and_has_end_date_exits(sdk, profile, file_event_namespace):
    file_event_namespace.saved_search = "abc"
    file_event_namespace.end = "end date"
    with pytest.raises(SystemExit):
        main.write_to(sdk, profile, file_event_namespace)


def test_validation_when_is_saved_search_and_has_exposure_types_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.saved_search = "abc"
    file_event_namespace.type = [ExposureTypeOptions.SHARED_TO_DOMAIN]
    with pytest.raises(SystemExit):
        main.send_to(sdk, profile, file_event_namespace)


def test_validation_when_is_saved_search_and_uses_checkpoint_mode_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.saved_search = "abc"
    file_event_namespace.use_checkpoint = "foo"
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


def test_validation_when_is_saved_search_and_has_include_non_exposure_exits(
    sdk, profile, file_event_namespace
):
    file_event_namespace.saved_search = "abc"
    file_event_namespace.include_non_exposure = True
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)


@pytest.mark.parametrize(
    "arg",
    [
        "c42_username",
        "actor",
        "md5",
        "sha256",
        "source",
        "file_name",
        "file_path",
        "process_owner",
        "tab_url",
    ],
)
def test_validation_when_is_saved_search_and_other_incompatible_multi_narg_argument_passed(
    sdk, profile, file_event_namespace, arg
):
    file_event_namespace.saved_search = "abc"
    setattr(file_event_namespace, arg, ["test_value"])
    with pytest.raises(SystemExit):
        main.print_out(sdk, profile, file_event_namespace)
