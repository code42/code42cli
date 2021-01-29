import pytest
from tests.integration.util import assert_test_is_successful

LEGAL_HOLD_COMMAND = "legal-hold"


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        "{} list".format(LEGAL_HOLD_COMMAND),
        "{} show 984140047896012577".format(LEGAL_HOLD_COMMAND),
        "{} list -f CSV".format(LEGAL_HOLD_COMMAND),
        "{} list -f TABLE".format(LEGAL_HOLD_COMMAND),
        "{} list -f RAW-JSON".format(LEGAL_HOLD_COMMAND),
        "{} list -f JSON".format(LEGAL_HOLD_COMMAND),
        "{} list --format CSV".format(LEGAL_HOLD_COMMAND),
        "{} list --format TABLE".format(LEGAL_HOLD_COMMAND),
        "{} list --format JSON".format(LEGAL_HOLD_COMMAND),
        "{} list --format RAW-JSON".format(LEGAL_HOLD_COMMAND),
    ],
)
def test_alert_rules_command_returns_success_return_code(
    runner, integration_test_profile, command
):
    assert_test_is_successful(runner, integration_test_profile, command)
