import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful


@pytest.mark.integration
def test_alert_rules_list_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = "alert-rules list"
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
def test_alert_rules_show_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = ("alert-rules show test-rule-id",)
    assert_test_is_successful(runner, append_profile(command))
