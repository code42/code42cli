import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.detectionlists import (
    DetectionList,
    DetectionListHandlers,
    get_user_id,
    update_user,
)
from .conftest import TEST_ID


_NAMESPACE = "{}.cmds.detectionlists".format(PRODUCT_NAME)


@pytest.fixture
def bulk_template_generator(mocker):
    return mocker.patch("{}.generate_template".format(_NAMESPACE))


@pytest.fixture
def bulk_processor(mocker):
    return mocker.patch("{}.run_bulk_process".format(_NAMESPACE))


def test_get_user_id_when_user_does_not_exist_exits(sdk_without_user):
    with pytest.raises(SystemExit):
        get_user_id(sdk_without_user, "risky employee")


def test_get_user_id_when_user_does_not_exist_print_error(sdk_without_user, capsys):
    try:
        get_user_id(sdk_without_user, "risky employee")
    except SystemExit:
        capture = capsys.readouterr()
        assert "ERROR: User 'risky employee' does not exist." in capture.out


def test_update_user_adds_cloud_aliases(sdk_with_user, profile):
    update_user(
        sdk_with_user, TEST_ID, cloud_alias=["1@example.com", "2@example.com", "3@example.com"]
    )
    sdk_with_user.detectionlists.add_user_cloud_aliases.assert_called_once_with(
        TEST_ID, ["1@example.com", "2@example.com", "3@example.com"]
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


class TestDetectionList(object):
    def test_load_commands_loads_expected_commands(self):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        cmds = detection_list.load_subcommands()
        assert cmds[0].name == "bulk"
        assert cmds[1].name == "add"

    def test_generate_template_file_generates_template(self, bulk_template_generator):
        def test_func():
            pass
        handlers = DetectionListHandlers()
        handlers.add_employee = test_func
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_template_file("add", path)
        bulk_template_generator.assert_called_once_with(test_func, path)

    def test_generate_template_file_when_given_remove_generates_expected_template(
        self, bulk_template_generator
    ):
        handlers = DetectionListHandlers()
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_template_file("remove", path)
        bulk_template_generator.assert_called_once_with(None, path)

    def test_bulk_add_employees_uses_csv_path(self, sdk, profile, bulk_processor):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_add_employees(sdk, profile, "csv_test")
        assert bulk_processor.call_args[0][0] == "csv_test"

    def test_bulk_remove_employees_uses_file_path(self, sdk, profile, bulk_processor):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_remove_employees(sdk, profile, "file_test")
        assert bulk_processor.call_args[0][0] == "file_test"
