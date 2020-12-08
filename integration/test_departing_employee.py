
import pytest
from integration import run_command

DEPARTING_EMPLOYEE_COMMAND = "code42 departing-employee"


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (f"{DEPARTING_EMPLOYEE_COMMAND} add", "Missing argument 'USERNAME'."),
        (f"{DEPARTING_EMPLOYEE_COMMAND} remove", "Missing argument 'USERNAME'."),
        (f"{DEPARTING_EMPLOYEE_COMMAND} bulk add", "Missing argument 'CSV_FILE'."),
        (f"{DEPARTING_EMPLOYEE_COMMAND} bulk remove", "Missing argument 'FILE'."),
    ]
)
def test_departing_employee_command_returns_error_exit_status_when_missing_required_parameters(
    command, error_msg
):
    return_code, response = run_command(command)
    assert return_code == 2
    assert error_msg in "".join(response)


"""
def test_departing_employee_add_user_command(command):
    pass


def test_departing_employee_remove_user_command(command):
    pass


def test_departing_employee_bulk_command(command):
    pass
"""
