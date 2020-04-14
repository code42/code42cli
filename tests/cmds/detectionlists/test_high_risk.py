import pytest

from code42cli.cmds.detectionlists.high_risk import (
    generate_csv_file,
    add_high_risk_employee,
    bulk_add_high_risk_employees,
)


@pytest.fixture
def bulk_template_generator(mocker):
    return mocker.patch("code42cli.cmds.detectionlists.high_risk.generate_template")


def test_generate_csv_file_generates_template(bulk_template_generator):
    path = "some/path"
    generate_csv_file("add", path)
    bulk_template_generator.assert_called_once_with(add_high_risk_employee, path)


def test_bulk_add_high_risk_employees_runs(mocker, bulk_processor, sdk, profile):
    factory = mocker.patch("code42cli.cmds.detectionlists.high_risk.create_bulk_processor")
    factory.return_value = bulk_processor
    bulk_add_high_risk_employees(sdk, profile, "")
    assert bulk_processor.run.call_count == 1


def test_bulk_add_high_risk_employees_creates_processor(mocker, bulk_processor, sdk, profile):
    factory = mocker.patch("code42cli.cmds.detectionlists.high_risk.create_bulk_processor")
    factory.return_value = bulk_processor
    bulk_add_high_risk_employees(sdk, profile, "csv_test")
    assert factory.call_args[0][0] == "csv_test"
