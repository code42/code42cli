import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful

CASES_COMMAND = "cases"


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        "{} list".format(CASES_COMMAND),
        "{} list -f TABLE".format(CASES_COMMAND),
        "{} list -f RAW-JSON".format(CASES_COMMAND),
        "{} list -f JSON".format(CASES_COMMAND),
        "{} list --format CSV".format(CASES_COMMAND),
        "{} list --format TABLE".format(CASES_COMMAND),
        "{} list --format JSON".format(CASES_COMMAND),
        "{} list --format RAW-JSON".format(CASES_COMMAND),
        "{} list --assignee 123".format(CASES_COMMAND),
        "{} list --status OPEN".format(CASES_COMMAND),
        "{} list --subject 123".format(CASES_COMMAND),
        "{} list --begin-create-time 2021-01-01".format(CASES_COMMAND),
        "{} list --end-create-time 2021-01-01".format(CASES_COMMAND),
        "{} list --begin-update-time 2021-01-01".format(CASES_COMMAND),
        "{} list --end-update-time 2021-01-01".format(CASES_COMMAND),
        "{} list --name test".format(CASES_COMMAND),
    ],
)
def test_cases_list_command_returns_success_return_code(
    runner, integration_test_profile, command
):
    assert_test_is_successful(runner, integration_test_profile, append_profile(command))
