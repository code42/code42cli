import pytest

LEGAL_HOLD_COMMAND = "code42 legal-hold"


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
def test_alert_rules_command_returns_success_return_code(command, command_runner):
    return_code, response = command_runner(command)
    assert return_code == 0
