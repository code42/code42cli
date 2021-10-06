import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful


@pytest.mark.integration
def test_users_list_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = "users list"
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
def test_users_orgs_list_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = "users orgs list"
    assert_test_is_successful(runner, append_profile(command))
