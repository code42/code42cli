import pytest

from code42cli.cmds.detectionlists.high_risk_employee import add_high_risk_employee


_TEST_ID = "TEST_ID"


@pytest.fixture
def sdk_with_user(sdk):
    sdk.users.get_by_username.return_value = {"users": [{"userUid": _TEST_ID}]}
    return sdk


def test_add_high_risk_employee_when_given_cloud_aliases_adds_alias(sdk_with_user, profile):
    alias = "risk employee alias"
    add_high_risk_employee(sdk_with_user, profile, "risky employee", cloud_aliases=[alias])
    sdk_with_user.detectionlists.add_user_cloud_aliases.assert_called_once_with(_TEST_ID, [alias])


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
        _TEST_ID, ["1@example.com", "2@example.com", "3@example.com"]
    )


def test_add_high_risk_employee_when_given_risk_factors_adds_tags(sdk_with_user, profile):
    add_high_risk_employee(sdk_with_user, profile, "risky employee", risk_factors="RF1 RF2 RF3")
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        _TEST_ID, ["RF1", "RF2", "RF3"]
    )


def test_add_high_risk_employee_when_given_str_of_risk_factors_adds_tags(sdk_with_user, profile):
    risk_factor = "BeingRisky"
    add_high_risk_employee(sdk_with_user, profile, "risky employee", risk_factors=[risk_factor])
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(_TEST_ID, [risk_factor])


def test_add_high_risk_employee_when_given_notes_updates_notes(sdk_with_user, profile):
    notes = "being risky"
    add_high_risk_employee(sdk_with_user, profile, "risky employee", notes=notes)
    sdk_with_user.detectionlists.update_user_notes.assert_called_once_with(_TEST_ID, notes)


def test_add_high_risk_employee_adds(sdk_with_user, profile):
    add_high_risk_employee(sdk_with_user, profile, "risky employee")
    sdk_with_user.detectionlists.high_risk_employee.add.assert_called_once_with(_TEST_ID)
