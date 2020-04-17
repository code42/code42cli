import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.detectionlists import DetectionList, DetectionListHandlers, get_user_id


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


def test_get_user_id_when_user_does_not_exist_exits(sdk_without_user, capsys):
    try:
        get_user_id(sdk_without_user, "risky employee")
    except SystemExit:
        capture = capsys.readouterr()
        assert "ERROR: User 'risky employee' does not exist." in capture.out


class TestDetectionList(object):
    def test_load_commands_loads_expected_commands(self):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        cmds = detection_list.load_subcommands()
        assert cmds[0].name == "bulk"
        assert cmds[1].name == "add"

    def test_generate_csv_file_generates_template(self, bulk_template_generator):
        handlers = DetectionListHandlers()
        detection_list = DetectionList("TestList", handlers)
        path = "some/path"
        detection_list.generate_csv_file("add", path)
        bulk_template_generator.assert_called_once_with(handlers.add_employee, path)

    def test_bulk_add_employees_uses_csv_path(self, sdk, profile, bulk_processor):
        detection_list = DetectionList("TestList", DetectionListHandlers())
        detection_list.bulk_add_employees(sdk, profile, "csv_test")
        assert bulk_processor.call_args[0][0] == "csv_test"
