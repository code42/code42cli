import json

import pytest
from pandas import DataFrame
from py42.response import Py42Response
from requests import Response

from code42cli.cmds.users import _add_legal_hold_membership_to_user_dataframe
from code42cli.main import cli


TEST_ROLE_RETURN_DATA = {
    "data": [{"roleName": "Customer Cloud Admin", "roleId": "1234543"}]
}
TEST_USERS_RESPONSE = {
    "users": [
        {
            "firstName": "test",
            "lastName": "username",
            "orgId": 4321,
            "orgUid": "44444444",
            "orgName": "ORG_NAME",
            "status": "Active",
            "notes": "This is a note.",
            "active": True,
            "blocked": False,
            "creationDate": "2021-03-12T20:07:40.898Z",
            "modificationDate": "2021-03-12T20:07:40.938Z",
            "userId": 1234,
            "username": "test.username@example.com",
            "userUid": "911162111513111325",
            "invited": False,
            "quotaInBytes": 55555,
        }
    ]
}
TEST_MATTER_RESPONSE = {
    "legalHolds": [
        {"legalHoldUid": "123456789", "name": "Legal Hold #1", "active": True},
        {"legalHoldUid": "987654321", "name": "Legal Hold #2", "active": True},
    ]
}
TEST_CUSTODIANS_RESPONSE = {
    "legalHoldMemberships": [
        {
            "legalHoldMembershipUid": "99999",
            "active": True,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {"legalHoldUid": "123456789", "name": "Legal Hold #1"},
            "user": {
                "userUid": "911162111513111325",
                "username": "test.username@example.com",
                "email": "test.username@example.com",
                "userExtRef": None,
            },
        },
        {
            "legalHoldMembershipUid": "11111",
            "active": True,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {"legalHoldUid": "987654321", "name": "Legal Hold #2"},
            "user": {
                "userUid": "911162111513111325",
                "username": "test.username@example.com",
                "email": "test.username@example.com",
                "userExtRef": None,
            },
        },
    ]
}

TEST_EMPTY_USERS_RESPONSE = {"users": []}
TEST_USERNAME = TEST_USERS_RESPONSE["users"][0]["username"]
TEST_USER_ID = TEST_USERS_RESPONSE["users"][0]["userId"]
TEST_ROLE_NAME = TEST_ROLE_RETURN_DATA["data"][0]["roleName"]


def _create_py42_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return Py42Response(response)


def get_all_users_generator():
    yield TEST_USERS_RESPONSE


def matter_list_generator():
    yield TEST_MATTER_RESPONSE


def custodian_list_generator():
    yield TEST_CUSTODIANS_RESPONSE


@pytest.fixture
def get_available_roles_response(mocker):
    return _create_py42_response(mocker, json.dumps(TEST_ROLE_RETURN_DATA))


@pytest.fixture
def get_all_users_success(cli_state):
    cli_state.sdk.users.get_all.return_value = get_all_users_generator()


@pytest.fixture
def get_user_id_success(cli_state):
    cli_state.sdk.users.get_by_username.return_value = TEST_USERS_RESPONSE


@pytest.fixture
def get_user_id_failure(cli_state):
    cli_state.sdk.users.get_by_username.return_value = TEST_EMPTY_USERS_RESPONSE


@pytest.fixture
def get_all_matter_success(cli_state):
    cli_state.sdk.legalhold.get_all_matters.return_value = matter_list_generator()


@pytest.fixture
def get_all_custodian_success(cli_state):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        custodian_list_generator()
    )


@pytest.fixture
def get_available_roles_success(cli_state, get_available_roles_response):
    cli_state.sdk.users.get_available_roles.return_value = get_available_roles_response


def test_list_when_non_table_format_outputs_expected_columns(
    runner, cli_state, get_all_users_success
):
    result = runner.invoke(cli, ["users", "list", "-f", "CSV"], obj=cli_state)
    assert "firstName" in result.output
    assert "lastName" in result.output
    assert "orgId" in result.output
    assert "orgUid" in result.output
    assert "orgName" in result.output
    assert "status" in result.output
    assert "notes" in result.output
    assert "active" in result.output
    assert "blocked" in result.output
    assert "creationDate" in result.output
    assert "modificationDate" in result.output
    assert "userId" in result.output
    assert "username" in result.output
    assert "userUid" in result.output
    assert "invited" in result.output
    assert "quotaInBytes" in result.output


def test_list_when_table_format_outputs_expected_columns(
    runner, cli_state, get_all_users_success
):
    result = runner.invoke(cli, ["users", "list", "-f", "TABLE"], obj=cli_state)
    assert "orgUid" in result.output
    assert "status" in result.output
    assert "username" in result.output
    assert "userUid" in result.output

    assert "firstName" not in result.output
    assert "lastName" not in result.output
    assert "orgId" not in result.output
    assert "orgName" not in result.output
    assert "notes" not in result.output
    assert "active" not in result.output
    assert "blocked" not in result.output
    assert "creationDate" not in result.output
    assert "modificationDate" not in result.output
    assert "userId" not in result.output
    assert "invited" not in result.output
    assert "quotaInBytes" not in result.output


def test_list_users_calls_users_get_all_with_expected_role_id(
    runner, cli_state, get_available_roles_success, get_all_users_success
):
    ROLE_NAME = "Customer Cloud Admin"
    runner.invoke(cli, ["users", "list", "--role-name", ROLE_NAME], obj=cli_state)
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=None, org_uid=None, role_id="1234543"
    )


def test_list_users_calls_get_all_users_with_correct_parameters(
    runner, cli_state, get_all_users_success
):
    org_uid = "TEST_ORG_UID"
    runner.invoke(
        cli, ["users", "list", "--org-uid", org_uid, "--active"], obj=cli_state
    )
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=True, org_uid=org_uid, role_id=None
    )


def test_list_users_when_given_inactive_uses_active_equals_false(
    runner, cli_state, get_available_roles_success, get_all_users_success
):
    runner.invoke(cli, ["users", "list", "--inactive"], obj=cli_state)
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=False, org_uid=None, role_id=None
    )


def test_list_users_when_given_active_and_inactive_raises_error(
    runner, cli_state, get_available_roles_success, get_all_users_success
):
    result = runner.invoke(
        cli, ["users", "list", "--active", "--inactive"], obj=cli_state
    )
    assert "Error: --inactive can't be used with: --active" in result.output


def test_list_users_when_given_excluding_active_and_inactive_uses_active_equals_none(
    runner, cli_state, get_available_roles_success, get_all_users_success
):
    runner.invoke(cli, ["users", "list"], obj=cli_state)
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=None, org_uid=None, role_id=None
    )


def test_add_legal_hold_membership_to_user_dataframe_adds_legal_hold_columns_to_dataframe(
    cli_state, get_all_matter_success, get_all_custodian_success
):
    testdf = DataFrame.from_records(
        [{"userUid": "840103986007089121", "status": "Active"}]
    )
    result = _add_legal_hold_membership_to_user_dataframe(cli_state.sdk, testdf)
    assert "legalHoldUid" in result.columns
    assert "legalHoldName" in result.columns


def test_list_include_legal_hold_membership_merges_in_and_concats_legal_hold_info(
    runner,
    cli_state,
    get_all_users_success,
    get_all_custodian_success,
    get_all_matter_success,
):
    result = runner.invoke(
        cli, ["users", "list", "--include-legal-hold-membership"], obj=cli_state
    )

    assert "Legal Hold #1,Legal Hold #2" in result.output
    assert "123456789,987654321" in result.output


def test_add_user_role_adds(
    runner, cli_state, get_user_id_success, get_available_roles_success
):
    command = [
        "users",
        "add-role",
        "--username",
        "test.username@example.com",
        "--role-name",
        "Customer Cloud Admin",
    ]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.users.add_role.assert_called_once_with(TEST_USER_ID, TEST_ROLE_NAME)


def test_add_user_role_raises_error_when_role_does_not_exist(
    runner, cli_state, get_user_id_success, get_available_roles_success
):
    command = [
        "users",
        "add-role",
        "--username",
        "test.username@example.com",
        "--role-name",
        "test",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert "Role with name 'test' not found." in result.output


def test_add_user_role_raises_error_when_username_does_not_exist(
    runner, cli_state, get_user_id_failure, get_available_roles_success
):
    command = [
        "users",
        "add-role",
        "--username",
        "not_a_username@example.com",
        "--role-name",
        "Desktop User",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert "User 'not_a_username@example.com' does not exist." in result.output


def test_remove_user_role_removes(
    runner, cli_state, get_user_id_success, get_available_roles_success
):
    command = [
        "users",
        "remove-role",
        "--username",
        "test.username@example.com",
        "--role-name",
        "Customer Cloud Admin",
    ]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.users.remove_role.assert_called_once_with(
        TEST_USER_ID, TEST_ROLE_NAME
    )


def test_remove_user_role_raises_error_when_role_does_not_exist(
    runner, cli_state, get_user_id_success, get_available_roles_success
):
    command = [
        "users",
        "remove-role",
        "--username",
        "test.username@example.com",
        "--role-name",
        "test",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert "Role with name 'test' not found." in result.output


def test_remove_user_role_raises_error_when_username_does_not_exist(
    runner, cli_state, get_user_id_failure, get_available_roles_success
):
    command = [
        "users",
        "remove-role",
        "--username",
        "not_a_username@example.com",
        "--role-name",
        "Desktop User",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert "User 'not_a_username@example.com' does not exist." in result.output
