import pytest
from integration import run_command

HR_EMPLOYEE_COMMAND = "code42 high-risk-employee"


@pytest.mark.parametrize(
    "command, error_msg",
    [
        ("{} add".format(HR_EMPLOYEE_COMMAND), "Missing argument 'USERNAME'."),
        ("{} remove".format(HR_EMPLOYEE_COMMAND), "Missing argument 'USERNAME'."),
        ("{} bulk add".format(HR_EMPLOYEE_COMMAND), "Missing argument 'CSV_FILE'."),
        ("{} bulk remove".format(HR_EMPLOYEE_COMMAND), "Missing argument 'FILE'."),
        (
            "{} bulk add-risk-tags".format(HR_EMPLOYEE_COMMAND),
            "Missing argument 'CSV_FILE'.",
        ),
        (
            "{} bulk remove-risk-tags".format(HR_EMPLOYEE_COMMAND),
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
