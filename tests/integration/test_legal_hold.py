import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful


@pytest.mark.integration
@pytest.mark.parametrize(
    "command_option",
    [
        "-f CSV",
        "-f TABLE",
        "-f RAW-JSON",
        "-f JSON",
        "--format CSV",
        "--format TABLE",
        "--format JSON",
        "--format RAW-JSON",
    ],
)
def test_legal_hold_list_command_returns_success_return_code(
    runner, integration_test_profile, command_option
):
    command = "legal-hold list {}".format(command_option)
    assert_test_is_successful(runner, append_profile(command))


def test_legal_hold_show_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = ("legal-hold show 984140047896012577",)
    assert_test_is_successful(runner, append_profile(command))
