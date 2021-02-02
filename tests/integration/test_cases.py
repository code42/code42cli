import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful


@pytest.mark.integration
@pytest.mark.parametrize(
    "command_option",
    [
        "-f TABLE",
        "-f RAW-JSON",
        "-f JSON",
        "--format CSV",
        "--format TABLE",
        "--format JSON",
        "--format RAW-JSON",
        "--assignee 123",
        "--status OPEN",
        "--subject 123",
        "--begin-create-time 2021-01-01",
        "--end-create-time 2021-01-01",
        "--begin-update-time 2021-01-01",
        "--end-update-time 2021-01-01",
        "--name test",
    ],
)
def test_cases_list_command_returns_success_return_code(
    runner, integration_test_profile, command_option
):
    command = "cases list {}".format(command_option)
    assert_test_is_successful(runner, append_profile(command))
