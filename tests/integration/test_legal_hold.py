import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful


@pytest.mark.integration
def test_legal_hold_list_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = "legal-hold list"
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
def test_legal_hold_show_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = ("legal-hold show 984140047896012577",)
    assert_test_is_successful(runner, append_profile(command))
