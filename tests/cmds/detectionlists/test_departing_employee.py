import pytest

from code42cli.cmds.detectionlists.departing_employee import (
    add_departing_employee,
    remove_departing_employee,
)
from .conftest import TEST_ID


def test_add_departing_employee_when_given_cloud_aliases_adds_alias(sdk_with_user, profile):
    alias = "departing employee alias"
    add_departing_employee(sdk_with_user, profile, "departing employee", cloud_alias=[alias])
    sdk_with_user.detectionlists.add_user_cloud_aliases.assert_called_once_with(TEST_ID, [alias])


def test_add_departing_employee_when_given_str_of_cloud_aliases_adds_aliases(
    sdk_with_user, profile
):
    add_departing_employee(
        sdk_with_user,
        profile,
        "departing employee",
        cloud_alias="1@example.com 2@example.com 3@example.com",
    )
    sdk_with_user.detectionlists.add_user_cloud_aliases.assert_called_once_with(
        TEST_ID, ["1@example.com", "2@example.com", "3@example.com"]
    )


def test_add_departing_employee_when_given_notes_updates_notes(sdk_with_user, profile):
    notes = "is leaving"
    add_departing_employee(sdk_with_user, profile, "departing employee", notes=notes)
    sdk_with_user.detectionlists.update_user_notes.assert_called_once_with(TEST_ID, notes)


def test_add_departing_employee_adds(sdk_with_user, profile):
    add_departing_employee(
        sdk_with_user, profile, "departing employee", departure_date="2020-02-02"
    )
    sdk_with_user.detectionlists.departing_employee.add.assert_called_once_with(
        TEST_ID, "2020-02-02"
    )


def test_add_departing_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(SystemExit):
        add_departing_employee(sdk_without_user, profile, "departing employee")


def test_add_departing_employee_when_user_does_not_exist_prints_error(
    sdk_without_user, profile, capsys
):
    try:
        add_departing_employee(sdk_without_user, profile, "departing employee")
    except SystemExit:
        capture = capsys.readouterr()
        assert "ERROR: User 'departing employee' does not exist." in capture.out


def test_remove_departing_employee_calls_remove(sdk_with_user, profile):
    remove_departing_employee(sdk_with_user, profile, "departing employee")
    sdk_with_user.detectionlists.departing_employee.remove.assert_called_once_with(TEST_ID)


def test_remove_departing_employee_when_user_does_not_exist_exits(sdk_without_user, profile):
    with pytest.raises(SystemExit):
        remove_departing_employee(sdk_without_user, profile, "departing employee")


def test_remove_departing_employee_when_user_does_not_exist_prints_error(
    sdk_without_user, profile, capsys
):
    try:
        remove_departing_employee(sdk_without_user, profile, "departing employee")
    except SystemExit:
        capture = capsys.readouterr()
        assert "ERROR: User 'departing employee' does not exist." in capture.out
