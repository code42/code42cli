import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.detectionlists.high_risk import (
    generate_csv_file,
    add_high_risk_employee,
    bulk_add_high_risk_employees,
)


@pytest.fixture
def bulk_template_generator(mocker):
    return mocker.patch("{}.cmds.detectionlists.high_risk.generate_template".format(PRODUCT_NAME))


@pytest.fixture
def bulk_processor_factory(mocker, bulk_processor):
    factory = mocker.patch(
        "{}.cmds.detectionlists.high_risk.create_bulk_processor".format(PRODUCT_NAME)
    )
    factory.return_value = bulk_processor
    return factory


def test_generate_csv_file_generates_template(bulk_template_generator):
    path = "some/path"
    generate_csv_file("add", path)
    bulk_template_generator.assert_called_once_with(add_high_risk_employee, path)


def test_bulk_add_high_risk_employees_runs(sdk, profile, bulk_processor, bulk_processor_factory):
    bulk_add_high_risk_employees(sdk, profile, "")
    assert bulk_processor.run.call_count == 1


def test_bulk_add_high_risk_employees_creates_processor(sdk, profile, bulk_processor_factory):
    bulk_add_high_risk_employees(sdk, profile, "csv_test")
    assert bulk_processor_factory.call_args[0][0] == "csv_test"
