import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful


@pytest.mark.integration
@pytest.mark.parametrize(
    "command_option",
    [
        "",
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
def test_alert_rules_list_command_returns_success_return_code(
    runner, integration_test_profile, command_option
):
    command = "alert-rules list {}".format(command_option)
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
def test_alert_rules_show_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = ("alert-rules show test-rule-id",)
    assert_test_is_successful(runner, append_profile(command))
