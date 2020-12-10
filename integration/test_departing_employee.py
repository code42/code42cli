import pytest
from integration import run_command

DEPARTING_EMPLOYEE_COMMAND = "code42 departing-employee"


@pytest.mark.parametrize(
    "command, error_msg",
    [
        ("{} add".format(DEPARTING_EMPLOYEE_COMMAND), "Missing argument 'USERNAME'."),
        (
            "{} remove".format(DEPARTING_EMPLOYEE_COMMAND),
            "Missing argument 'USERNAME'.",
        ),
        (
            "{} bulk add".format(DEPARTING_EMPLOYEE_COMMAND),
            "Missing argument 'CSV_FILE'.",
        ),
        (
            "{} bulk remove".format(DEPARTING_EMPLOYEE_COMMAND),
            "Missing argument 'FILE'.",
        ),
    ],
)
def test_departing_employee_command_returns_error_exit_status_when_missing_required_parameters(
    command, error_msg
):
    return_code, response = run_command(command)
    assert return_code == 2
    assert error_msg in "".join(response)
