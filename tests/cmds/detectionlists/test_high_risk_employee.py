import pytest

from code42cli.errors import UserAlreadyAddedError, UnknownRiskTagError, UserDoesNotExistError
from code42cli.cmds.detectionlists.high_risk_employee import (
    add_high_risk_employee,
    remove_high_risk_employee,
    HighRiskEmployeeSubcommandLoader,
)

from code42cli.cmds.detectionlists.enums import RiskTags
from .conftest import TEST_ID

from py42.exceptions import Py42BadRequestError


_EMPLOYEE = "risky employee"


class TestHighRiskEmployeeSubcommandLoader(object):
    def test_load_subcommands_loads_expected_commands(self):
        loader = HighRiskEmployeeSubcommandLoader("test")
        cmds = loader.load_commands()
        names = [cmd.name for cmd in cmds]
        assert "add" in names
        assert "bulk" in names
        assert "remove" in names

    def test_loader_has_expected_detection_list_name(self):
        loader = HighRiskEmployeeSubcommandLoader("test")
        assert "high-risk-employee" == loader.detection_list.name


def test_add_high_risk_employee_when_given_cloud_alias_adds_alias(sdk_with_user, profile):
    alias = "risk employee alias"
    add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE, cloud_alias=alias)
    sdk_with_user.detectionlists.add_user_cloud_alias.assert_called_once_with(TEST_ID, alias)


def test_add_high_risk_employee_when_given_risk_tags_adds_tags(sdk_with_user, profile):
    add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE, risk_tag="tag1 tag2 tag3")
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, ["tag1", "tag2", "tag3"]
    )


def test_add_high_risk_employee_when_given_str_of_risk_tags_adds_tags(sdk_with_user, profile):
    risk_tag = "BeingRisky"
    add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE, risk_tag=[risk_tag])
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(TEST_ID, [risk_tag])


def test_add_high_risk_employee_when_given_notes_updates_notes(sdk_with_user, profile):
    notes = "being risky"
    add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE, notes=notes)
    sdk_with_user.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_add_high_risk_employee_adds(sdk_with_user, profile):
    add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)
    sdk_with_user.detectionlists.high_risk_employee.add.assert_called_once_with(TEST_ID)


def test_add_high_risk_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        add_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)


def test_add_high_risk_employee_when_user_already_added_raises_UserAlreadyAddedError(
    sdk_with_user, profile, bad_request_for_user_already_added
):
    sdk_with_user.detectionlists.high_risk_employee.add.side_effect = (
        bad_request_for_user_already_added
    )
    with pytest.raises(UserAlreadyAddedError):
        add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)


def test_add_high_risk_employee_when_bad_request_but_not_user_already_added_raises_Py42BadRequestError(
    sdk_with_user, profile, generic_bad_request, caplog
):
    sdk_with_user.detectionlists.high_risk_employee.add.side_effect = generic_bad_request
    with pytest.raises(Py42BadRequestError):
        add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)


def test_add_high_risk_employee_when_bad_request_and_unknown_risk_tags_raises_UnknownRiskTagError(
    sdk_with_user, profile, generic_bad_request
):
    sdk_with_user.detectionlists.add_user_risk_tags.side_effect = generic_bad_request
    foo = "foo"
    bar = "bar"
    mysterious_coffee_breaks = "MYSTERIOUS_COFFEE_BREAKS"
    try:
        add_high_risk_employee(
            sdk_with_user,
            profile,
            _EMPLOYEE,
            risk_tag="{} {} {} {} {} {} {}".format(
                RiskTags.ELEVATED_ACCESS_PRIVILEGES,
                foo,
                RiskTags.HIGH_IMPACT_EMPLOYEE,
                bar,
                mysterious_coffee_breaks,
                RiskTags.SUSPICIOUS_SYSTEM_ACTIVITY,
                RiskTags.CONTRACT_EMPLOYEE,
            ),
        )
    except UnknownRiskTagError as err:
        err_str = str(err)
        assert foo in err_str
        assert bar in err_str
        assert mysterious_coffee_breaks in err_str


def test_remove_high_risk_employee_calls_remove(sdk_with_user, profile):
    remove_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)
    sdk_with_user.detectionlists.high_risk_employee.remove.assert_called_once_with(TEST_ID)


def test_remove_high_risk_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        remove_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)
