import pytest
import logging

from code42cli.cmds.detectionlists import UserDoesNotExistError, UserAlreadyAddedError
from code42cli.cmds.detectionlists.high_risk_employee import (
    add_high_risk_employee,
    remove_high_risk_employee,
    add_risk_tags,
    remove_risk_tags,
)
from .conftest import TEST_ID

from py42.exceptions import Py42BadRequestError


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
    sdk_without_user, profile, caplog
):
    with caplog.at_level(logging.ERROR):
        try:
            add_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)
        except UserDoesNotExistError:
            assert str(UserDoesNotExistError(_EMPLOYEE)) in caplog.text


def test_add_high_risk_employee_when_user_already_added_raises_UserAlreadyAddedError(
    sdk_with_user, profile, bad_request_for_user_already_added
):
    sdk_with_user.detectionlists.high_risk_employee.add.side_effect = (
        bad_request_for_user_already_added
    )
    with pytest.raises(UserAlreadyAddedError):
        add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)


def test_add_high_risk_employee_when_bad_request_but_not_user_already_added_raises_Py42BadRequestError(
    sdk_with_user, profile, bad_request_for_other_reasons, caplog
):
    sdk_with_user.detectionlists.high_risk_employee.add.side_effect = bad_request_for_other_reasons
    with pytest.raises(Py42BadRequestError):
        add_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)


def test_remove_high_risk_employee_calls_remove(sdk_with_user, profile):
    remove_high_risk_employee(sdk_with_user, profile, _EMPLOYEE)
    sdk_with_user.detectionlists.high_risk_employee.remove.assert_called_once_with(TEST_ID)


def test_remove_high_risk_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        remove_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)


def test_remove_high_risk_employee_when_user_does_not_exist_prints_error(
    sdk_without_user, profile, caplog
):
    with caplog.at_level(logging.ERROR):
        try:
            remove_high_risk_employee(sdk_without_user, profile, _EMPLOYEE)
        except UserDoesNotExistError:
            assert str(UserDoesNotExistError(_EMPLOYEE)) in caplog.text


def test_add_risk_tags_adds_tags(sdk_with_user, profile):
    add_risk_tags(sdk_with_user, profile, _EMPLOYEE, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"])
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"]
    )


def test_add_risk_tags_when_given_space_delimited_str_adds_expected_tags(sdk_with_user, profile):
    add_risk_tags(sdk_with_user, profile, _EMPLOYEE, "TAG_YOU_ARE_IT GROUND_IS_LAVA")
    sdk_with_user.detectionlists.add_user_risk_tags.assert_called_once_with(
        TEST_ID, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"]
    )


def test_add_risk_tags_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        add_risk_tags(sdk_without_user, profile, _EMPLOYEE, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"])


def test_add_risk_tags_when_user_does_not_exist_prints_error(sdk_without_user, profile, caplog):
    with caplog.at_level(logging.ERROR):
        try:
            add_risk_tags(
                sdk_without_user, profile, _EMPLOYEE, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"]
            )
        except UserDoesNotExistError:
            assert str(UserDoesNotExistError(_EMPLOYEE)) in caplog.text


def test_remove_risk_tags_adds_tags(sdk_with_user, profile):
    remove_risk_tags(sdk_with_user, profile, _EMPLOYEE, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"])
    sdk_with_user.detectionlists.remove_user_risk_tags.assert_called_once_with(
        TEST_ID, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"]
    )


def test_remove_risk_tags_when_given_space_delimited_str_adds_expected_tags(sdk_with_user, profile):
    remove_risk_tags(sdk_with_user, profile, _EMPLOYEE, "TAG_YOU_ARE_IT GROUND_IS_LAVA")
    sdk_with_user.detectionlists.remove_user_risk_tags.assert_called_once_with(
        TEST_ID, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"]
    )


def test_remove_risk_tags_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        remove_risk_tags(sdk_without_user, profile, _EMPLOYEE, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"])


def test_remove_risk_tags_when_user_does_not_exist_prints_error(sdk_without_user, profile, caplog):
    with caplog.at_level(logging.ERROR):
        try:
            remove_risk_tags(
                sdk_without_user, profile, _EMPLOYEE, ["TAG_YOU_ARE_IT", "GROUND_IS_LAVA"]
            )
        except UserDoesNotExistError:
            assert str(UserDoesNotExistError(_EMPLOYEE)) in caplog.text
