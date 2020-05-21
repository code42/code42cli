import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.detectionlists import (
    try_handle_user_already_added_error,
    DetectionList,
    DetectionListHandlers,
    get_user_id,
    update_user,
    try_add_risk_tags,
    try_remove_risk_tags,
    add_risk_tags,
    remove_risk_tags,
)
from code42cli.errors import UserAlreadyAddedError, UnknownRiskTagError, UserDoesNotExistError
from code42cli.bulk import BulkCommandType
from code42cli.cmds.detectionlists.enums import RiskTags
from .conftest import TEST_ID
from ...conftest import create_mock_reader


_NAMESPACE = "{}.cmds.detectionlists".format(PRODUCT_NAME)
_EMPLOYEE = "risky employee"


@pytest.fixture
def bulk_template_generator(mocker):
    return mocker.patch("{}.generate_template".format(_NAMESPACE))


@pytest.fixture
def bulk_processor(mocker):
    return mocker.patch("{}.run_bulk_process".format(_NAMESPACE))


def test_try_handle_user_already_added_error_when_error_indicates_user_added_raises_UserAlreadyAddedError(
    bad_request_for_user_already_added
):
    with pytest.raises(UserAlreadyAddedError):
        try_handle_user_already_added_error(bad_request_for_user_already_added, "name", "listname")


def test_try_handle_user_already_added_error_when_error_does_not_indicate_user_added_returns_false(
    generic_bad_request
):
    assert not try_handle_user_already_added_error(generic_bad_request, "name", "listname")


def test_get_user_id_when_user_does_not_raise_error(sdk_without_user):
    with pytest.raises(UserDoesNotExistError):
        get_user_id(sdk_without_user, "risky employee")


def test_update_user_adds_cloud_alias(sdk_with_user, profile):
    update_user(sdk_with_user, TEST_ID, cloud_alias="1@example.com")
    sdk_with_user.detectionlists.add_user_cloud_alias.assert_called_once_with(
        TEST_ID, "1@example.com"
    )


def test_update_user_adds_risk_tags(sdk_with_user, profile):
    update_user(sdk_with_user, TEST_ID, risk_tag=["rf1", "rf2", "rf3"])
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, ["rf1", "rf2", "rf3"]
    )


def test_update_user_updates_notes(sdk_with_user, profile):
    notes = "notes"
    update_user(sdk_with_user, TEST_ID, notes=notes)
    sdk_with_user.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_try_add_risk_tags_when_sdk_raises_bad_request_and_given_unknown_tags_raises_UnknownRiskTagError(
    sdk, profile, generic_bad_request
):
    sdk.detectionlists.add_user_risk_tags.side_effect = generic_bad_request
    try:
        try_add_risk_tags(sdk, profile, ["foo", RiskTags.SUSPICIOUS_SYSTEM_ACTIVITY, "bar"])
    except UnknownRiskTagError as err:
        err_str = str(err)
        assert "foo" in err_str
        assert "bar" in err_str


def test_try_remove_risk_tags_when_sdk_raises_bad_request_and_given_unknown_tags_raises_UnknownRiskTagError(
    sdk, profile, generic_bad_request
):
    sdk.detectionlists.remove_user_risk_tags.side_effect = generic_bad_request
    try:
        try_remove_risk_tags(sdk, profile, ["foo", RiskTags.SUSPICIOUS_SYSTEM_ACTIVITY, "bar"])
    except UnknownRiskTagError as err:
        err_str = str(err)
        assert "foo" in err_str
        assert "bar" in err_str


class TestDetectionList(object):
    def test_load_commands_loads_expected_commands(self):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        cmds = detection_list.load_subcommands()
        assert cmds[0].name == "bulk"
        assert cmds[1].name == "add"
        assert cmds[2].name == "remove"

    def test_generate_template_file_when_given_add_generates_template_from_handler(
        self, bulk_template_generator
    ):
        def a_test_func(param1, param2, param3):
            pass

        handlers = DetectionListHandlers()
        handlers.add_employee = a_test_func
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_template_file(BulkCommandType.ADD, path)
        bulk_template_generator.assert_called_once_with(a_test_func, path)

    def test_generate_template_file_when_given_remove_generates_template_from_handler(
        self, bulk_template_generator
    ):
        def a_test_func():
            pass

        handlers = DetectionListHandlers()
        handlers.remove_employee = a_test_func
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_template_file(BulkCommandType.REMOVE, path)
        bulk_template_generator.assert_called_once_with(a_test_func, path)

    def test_bulk_add_employees_uses_expected_arguments(self, mocker, sdk, profile, bulk_processor):
        reader = create_mock_reader([{"test": "value"}])
        reader_factory = mocker.patch("{}.create_csv_reader".format(_NAMESPACE))
        reader_factory.return_value = reader
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_add_employees(sdk, profile, "csv_test")
        assert bulk_processor.call_args[0][1] == reader
        reader_factory.assert_called_once_with("csv_test")

    def test_bulk_remove_employees_uses_expected_arguments(
        self, mocker, sdk, profile, bulk_processor
    ):
        reader = create_mock_reader(["test1", "test2"])
        reader_factory = mocker.patch("{}.create_flat_file_reader".format(_NAMESPACE))
        reader_factory.return_value = reader
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_remove_employees(sdk, profile, "file_test")
        assert bulk_processor.call_args[0][1] == reader
        reader_factory.assert_called_once_with("file_test")

    def test_bulk_add_risk_tags_uses_csv_path(self, mocker, sdk, profile, bulk_processor):
        reader = create_mock_reader([{"test": "value"}])
        reader_factory = mocker.patch("{}.create_csv_reader".format(_NAMESPACE))
        reader_factory.return_value = reader
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_add_risk_tags(sdk, profile, "csv_test")
        assert bulk_processor.call_args[0][1] == reader
        reader_factory.assert_called_once_with("csv_test")

    def test_bulk_remove_risk_tags_uses_csv_path(self, mocker, sdk, profile, bulk_processor):
        reader = create_mock_reader([{"test": "value"}])
        reader_factory = mocker.patch("{}.create_csv_reader".format(_NAMESPACE))
        reader_factory.return_value = reader
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_remove_risk_tags(sdk, profile, "file_test")
        assert bulk_processor.call_args[0][1] == reader
        reader_factory.assert_called_once_with("file_test")


def test_add_risk_tags_adds_tags(sdk_with_user, profile):
    add_risk_tags(
        sdk_with_user,
        profile,
        _EMPLOYEE,
        [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK],
    )
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK]
    )


def test_add_risk_tags_when_given_space_delimited_str_adds_expected_tags(sdk_with_user, profile):
    add_risk_tags(
        sdk_with_user,
        profile,
        _EMPLOYEE,
        "{} {}".format(RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK),
    )
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK]
    )


def test_add_risk_tags_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        add_risk_tags(
            sdk_without_user,
            profile,
            _EMPLOYEE,
            [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK],
        )


def test_add_risk_tags_when_bad_request_and_unknown_risk_tags_raises_UnknownRiskTagError(
    sdk_with_user, profile, generic_bad_request
):
    sdk_with_user.detectionlists.add_user_risk_tags.side_effect = generic_bad_request
    try:
        add_risk_tags(
            sdk_with_user,
            profile,
            _EMPLOYEE,
            "{} foo {} bar".format(RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK),
        )
    except UnknownRiskTagError as err:
        err_str = str(err)
        assert "foo" in err_str
        assert "bar" in err_str


def test_remove_risk_tags_adds_tags(sdk_with_user, profile):
    remove_risk_tags(
        sdk_with_user,
        profile,
        _EMPLOYEE,
        [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK],
    )
    sdk_with_user.detectionlists.remove_user_risk_tags.assert_called_once_with(
        TEST_ID, [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK]
    )


def test_remove_risk_tags_when_given_space_delimited_str_adds_expected_tags(sdk_with_user, profile):
    remove_risk_tags(
        sdk_with_user,
        profile,
        _EMPLOYEE,
        "{} {}".format(RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK),
    )
    sdk_with_user.detectionlists.remove_user_risk_tags.assert_called_once_with(
        TEST_ID, [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK]
    )


def test_remove_risk_tags_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        remove_risk_tags(
            sdk_without_user,
            profile,
            _EMPLOYEE,
            [RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK],
        )


def test_remove_risk_tags_when_bad_request_and_unknown_risk_tags_raises_UnknownRiskTagError(
    sdk_with_user, profile, generic_bad_request
):
    sdk_with_user.detectionlists.remove_user_risk_tags.side_effect = generic_bad_request
    try:
        remove_risk_tags(
            sdk_with_user,
            profile,
            _EMPLOYEE,
            "{} foo {} bar".format(RiskTags.ELEVATED_ACCESS_PRIVILEGES, RiskTags.FLIGHT_RISK),
        )
    except UnknownRiskTagError as err:
        err_str = str(err)
        assert "foo" in err_str
        assert "bar" in err_str

