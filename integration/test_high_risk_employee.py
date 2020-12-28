import pytest
from integration import run_command

HR_EMPLOYEE_COMMAND = "code42 high-risk-employee"


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (f"{HR_EMPLOYEE_COMMAND} add", "Missing argument 'USERNAME'."),
        (f"{HR_EMPLOYEE_COMMAND} remove", "Missing argument 'USERNAME'."),
        (f"{HR_EMPLOYEE_COMMAND} bulk add", "Missing argument 'CSV_FILE'."),
        (f"{HR_EMPLOYEE_COMMAND} bulk remove", "Missing argument 'FILE'."),
        (f"{HR_EMPLOYEE_COMMAND} bulk add-risk-tags", "Missing argument 'CSV_FILE'."),
        (
            f"{HR_EMPLOYEE_COMMAND} bulk remove-risk-tags",
            "Missing argument 'CSV_FILE'.",
        ),
    ],
)
def test_hr_employee_command_returns_error_exit_status_when_missing_required_parameters(
    command, error_msg
):
    return_code, response = run_command(command)
    assert return_code == 2
    assert error_msg in "".join(response)
