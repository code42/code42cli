import pytest

from code42cli.cmds.detectionlists import UserDoesNotExistError
from code42cli.cmds.detectionlists.high_risk_employee import (
    add_high_risk_employee,
    remove_high_risk_employee,
)
from .conftest import TEST_ID


_EMPLOYEE = "risky employee"


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


def test_add_high_risk_employee_when_user_does_not_exist_prints_error(
    sdk_without_user, profile, capsys
):
    try:
        add_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)
    except UserDoesNotExistError:
        capture = capsys.readouterr()
        assert str(UserDoesNotExistError(_EMPLOYEE)) in capture.out


def test_remove_high_risk_employee_calls_remove(sdk_with_user, profile):
    remove_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)
    sdk_with_user.detectionlists.high_risk_employee.remove.assert_called_once_with(TEST_ID)


def test_remove_high_risk_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        remove_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)


def test_remove_high_risk_employee_when_user_does_not_exist_prints_error(
    sdk_without_user, profile, capsys
):
    try:
        remove_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)
    except UserDoesNotExistError:
        capture = capsys.readouterr()
        assert str(UserDoesNotExistError(_EMPLOYEE)) in capture.out
