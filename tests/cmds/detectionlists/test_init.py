import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.detectionlists import DetectionList, DetectionListHandlers


_NAMESPACE = "{}.cmds.detectionlists".format(PRODUCT_NAME)


@pytest.fixture
def bulk_template_generator(mocker):
    return mocker.patch("{}.generate_template".format(_NAMESPACE))


@pytest.fixture
def bulk_processor(mocker):
    return mocker.patch("{}.run_bulk_process".format(_NAMESPACE))


class TestDetectionList(object):
    def test_load_commands_loads_expected_commands(self):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        cmds = detection_list.load_subcommands()
        assert cmds[0].name == "bulk"
        assert cmds[1].name == "add"

    def test_generate_csv_file_when_given_add_generates_expected_template(
        self, bulk_template_generator
    ):
        handlers = DetectionListHandlers()
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_csv_file("add", path)
        bulk_template_generator.assert_called_once_with(handlers.add_employee, path)

    def test_generate_csv_file_when_given_remove_generates_expected_template(
        self, bulk_template_generator
    ):
        handlers = DetectionListHandlers()
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_csv_file("remove", path)
        bulk_template_generator.assert_called_once_with(handlers.remove_employee, path)

    def test_bulk_add_employees_uses_csv_path(self, sdk, profile, bulk_processor):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_add_employees(sdk, profile, "csv_test")
        assert bulk_processor.call_args[0][0] == "csv_test"

    def test_bulk_remove_employees_uses_csv_path(self, sdk, profile, bulk_processor):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_remove_employees(sdk, profile, "file_test")
        assert bulk_processor.call_args[0][0] == "file_test"
