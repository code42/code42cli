import pytest

from code42cli.cmds.detectionlists.high_risk_employee import add_high_risk_employee
from .conftest import TEST_ID


def test_add_high_risk_employee_when_given_cloud_aliases_adds_alias(sdk_with_user, profile):
    alias = "risk employee alias"
    add_high_risk_employee(sdk_with_user, profile, "risky employee", cloud_aliases=[alias])
    sdk_with_user.detectionlists.add_user_cloud_aliases.assert_called_once_with(TEST_ID, [alias])


def test_add_high_risk_employee_when_given_str_of_cloud_aliases_adds_aliases(
    sdk_with_user, profile
):
    add_high_risk_employee(
        sdk_with_user,
        profile,
        "risky employee",
        cloud_aliases="1@example.com 2@example.com 3@example.com",
    )
    sdk_with_user.detectionlists.add_user_cloud_aliases.assert_called_once_with(
        TEST_ID, ["1@example.com", "2@example.com", "3@example.com"]
    )


def test_add_high_risk_employee_when_given_risk_factors_adds_tags(sdk_with_user, profile):
    add_high_risk_employee(sdk_with_user, profile, "risky employee", risk_factors="RF1 RF2 RF3")
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, ["RF1", "RF2", "RF3"]
    )


def test_add_high_risk_employee_when_given_str_of_risk_factors_adds_tags(sdk_with_user, profile):
    risk_factor = "BeingRisky"
    add_high_risk_employee(sdk_with_user, profile, "risky employee", risk_factors=[risk_factor])
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(TEST_ID, [risk_factor])


def test_add_high_risk_employee_when_given_notes_updates_notes(sdk_with_user, profile):
    notes = "being risky"
    add_high_risk_employee(sdk_with_user, profile, "risky employee", notes=notes)
    sdk_with_user.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_add_high_risk_employee_adds(sdk_with_user, profile):
    add_high_risk_employee(sdk_with_user, profile, "risky employee")
    sdk_with_user.detectionlists.high_risk_employee.add.assert_called_once_with(TEST_ID)


def test_add_high_risk_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(SystemExit):
        add_high_risk_employee(sdk_without_user, profile, "risky employee")


def test_add_high_risk_employee_when_user_does_not_exist_exits(sdk_without_user, profile, capsys):
    try:
        add_high_risk_employee(sdk_without_user, profile, "risky employee")
    except SystemExit:
        capture = capsys.readouterr()
        assert "ERROR: User 'risky employee' does not exist." in capture.out
