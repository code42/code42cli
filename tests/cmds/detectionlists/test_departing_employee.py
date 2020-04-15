import pytest

from code42cli.cmds.detectionlists.departing_employee import (
    generate_csv_file,
    add_departing_employee,
    bulk_add_departing_employees,
)
from .conftest import DetectionListMockFactory


@pytest.fixture
def detection_list_mocks(mocker):
    return DetectionListMockFactory(mocker, "departing_employee")


@pytest.fixture
def bulk_template_generator(detection_list_mocks):
    return detection_list_mocks.create_bulk_template_generator()


@pytest.fixture
def bulk_processor(detection_list_mocks):
    return detection_list_mocks.create_bulk_processor()


def test_generate_csv_file_generates_template(bulk_template_generator):
    path = "some/path"
    generate_csv_file("add", path)
    bulk_template_generator.assert_called_once_with(add_departing_employee, path)


def test_bulk_add_high_risk_employees_uses_csv_path(sdk, profile, bulk_processor):
    bulk_add_departing_employees(sdk, profile, "csv_test")
    assert bulk_processor.call_args[0][0] == "csv_test"
