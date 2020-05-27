import pytest

from code42cli.errors import UserAlreadyAddedError, UserDoesNotExistError
from code42cli.cmds.detectionlists.departing_employee import (
    add_departing_employee,
    remove_departing_employee,
    DepartingEmployeeSubcommandLoader,
)

from .conftest import TEST_ID

from py42.exceptions import Py42BadRequestError


_EMPLOYEE = "departing employee"


class TestDepartingEmployeeSubcommandLoader(object):
    def test_load_subcommands_loads_expected_commands(self):
        loader = DepartingEmployeeSubcommandLoader("test")
        cmds = loader.load_commands()
        names = [cmd.name for cmd in cmds]
        assert "add" in names
        assert "bulk" in names
        assert "remove" in names
    
    def test_loader_has_expected_detection_list_name(self):
        loader = DepartingEmployeeSubcommandLoader("test")
        assert "departing-employee" == loader.detection_list.name


def test_add_departing_employee_when_given_cloud_alias_adds_alias(sdk_with_user, profile):
    alias = "departing employee alias"
    add_departing_employee(sdk_with_user, profile, _EMPLOYEE, cloud_alias=[alias])
    sdk_with_user.detectionlists.add_user_cloud_alias.assert_called_once_with(TEST_ID, [alias])


def test_add_departing_employee_when_given_notes_updates_notes(sdk_with_user, profile):
    notes = "is leaving"
    add_departing_employee(sdk_with_user, profile, _EMPLOYEE, notes=notes)
    sdk_with_user.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_add_departing_employee_adds(sdk_with_user, profile):
    add_departing_employee(sdk_with_user, profile, _EMPLOYEE, departure_date="2020-02-02")
    sdk_with_user.detectionlists.departing_employee.add.assert_called_once_with(
        TEST_ID, "2020-02-02"
    )


def test_add_departing_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        add_departing_employee(sdk_without_user, profile, _EMPLOYEE)


def test_add_departing_employee_when_user_already_added_raises_UserAlreadyAddedError(
    sdk_with_user, profile, bad_request_for_user_already_added
):
    sdk_with_user.detectionlists.departing_employee.add.side_effect = (
        bad_request_for_user_already_added
    )
    with pytest.raises(UserAlreadyAddedError):
        add_departing_employee(sdk_with_user, profile, _EMPLOYEE)


def test_add_departing_employee_when_bad_request_but_not_user_already_added_raises_Py42BadRequestError(
    sdk_with_user, profile, generic_bad_request, caplog
):
    sdk_with_user.detectionlists.departing_employee.add.side_effect = generic_bad_request
    with pytest.raises(Py42BadRequestError):
        add_departing_employee(sdk_with_user, profile, _EMPLOYEE)


def test_remove_departing_employee_calls_remove(sdk_with_user, profile):
    remove_departing_employee(sdk_with_user, profile, _EMPLOYEE)
    sdk_with_user.detectionlists.departing_employee.remove.assert_called_once_with(TEST_ID)


def test_remove_departing_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(UserDoesNotExistError):
        remove_departing_employee(sdk_without_user, profile, _EMPLOYEE)
