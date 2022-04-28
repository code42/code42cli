import datetime
import json

import pytest
from py42.exceptions import Py42ActiveLegalHoldError
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42CloudAliasCharacterLimitExceededError
from py42.exceptions import Py42CloudAliasLimitExceededError
from py42.exceptions import Py42InvalidEmailError
from py42.exceptions import Py42InvalidPasswordError
from py42.exceptions import Py42InvalidUsernameError
from py42.exceptions import Py42NotFoundError
from py42.exceptions import Py42OrgNotFoundError
from py42.exceptions import Py42UserRiskProfileNotFound
from tests.conftest import create_mock_http_error
from tests.conftest import create_mock_response

from code42cli.main import cli
from code42cli.worker import WorkerStats

_NAMESPACE = "code42cli.cmds.users"
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
            "roles": ["Desktop User"],
            "userId": 1234,
            "username": "test.username@example.com",
            "userUid": "911162111513111325",
            "invited": False,
            "quotaInBytes": 55555,
        }
    ]
}
TEST_USER_RESPONSE = {
    "tenantId": "SampleTenant1",
    "userId": 12345,
    "userName": "Sample.User1@samplecase.com",
    "displayName": "Sample User1",
    "notes": "This is an example of notes about Sample User1.",
    "cloudAliases": ["Sample.User1@samplecase.com", "Sample.User1@gmail.com"],
    "managerUid": 12345,
    "managerUsername": "manager.user1@samplecase.com",
    "managerDisplayName": "Manager Name",
    "title": "Software Engineer",
    "division": "Engineering",
    "department": "Research and Development",
    "employmentType": "Full-time",
    "city": "Anytown",
    "state": "MN",
    "country": "US",
    "riskFactors": ["FLIGHT_RISK", "HIGH_IMPACT_EMPLOYEE"],
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
TEST_EMPTY_CUSTODIANS_RESPONSE = {"legalHoldMemberships": []}
TEST_EMPTY_MATTERS_RESPONSE = {"legalHolds": []}
TEST_EMPTY_USERS_RESPONSE = {"users": []}
TEST_USERNAME = TEST_USERS_RESPONSE["users"][0]["username"]
TEST_ALIAS = TEST_USER_RESPONSE["cloudAliases"][0]
TEST_USER_ID = TEST_USERS_RESPONSE["users"][0]["userId"]
TEST_USER_UID = TEST_USER_RESPONSE["userId"]
TEST_ROLE_NAME = TEST_ROLE_RETURN_DATA["data"][0]["roleName"]
TEST_GET_ORG_RESPONSE = {
    "orgId": 9087,
    "orgUid": "1007759454961904673",
    "orgGuid": "a9578c3d-736b-4d96-80e5-71edd8a11ea3",
    "orgName": "19may",
    "orgExtRef": None,
    "notes": None,
    "status": "Active",
    "active": True,
    "blocked": False,
    "parentOrgId": 2689,
    "parentOrgUid": "890854247383106706",
    "parentOrgGuid": "8c97h74umc2s8mmm",
    "type": "ENTERPRISE",
    "classification": "BASIC",
    "externalId": "1007759454961904673",
    "hierarchyCounts": {},
    "configInheritanceCounts": {},
    "creationDate": "2021-05-19T10:10:43.459Z",
    "modificationDate": "2021-05-20T14:43:42.276Z",
    "deactivationDate": None,
    "settings": {"maxSeats": None, "maxBytes": None},
    "settingsInherited": {"maxSeats": "", "maxBytes": ""},
    "settingsSummary": {"maxSeats": "", "maxBytes": ""},
    "registrationKey": "72RU-8P9S-M7KK-RHCC",
    "reporting": {"orgManagers": []},
    "customConfig": False,
}
TEST_EMPTY_ORGS_RESPONSE = {"totalCount": 0, "orgs": []}
TEST_GET_ALL_ORGS_RESPONSE = {"totalCount": 1, "orgs": [TEST_GET_ORG_RESPONSE]}
TEST_ORG_UID = "1007759454961904673"


@pytest.fixture
def update_user_response(mocker):
    return create_mock_response(mocker)


@pytest.fixture
def get_available_roles_response(mocker):
    return create_mock_response(mocker, data=TEST_ROLE_RETURN_DATA)


@pytest.fixture
def get_users_response(mocker):
    return create_mock_response(mocker, data=TEST_USERS_RESPONSE)


@pytest.fixture
def get_user_response(mocker):
    return create_mock_response(mocker, data=TEST_USER_RESPONSE)


@pytest.fixture
def get_user_failure(mocker):
    return Py42UserRiskProfileNotFound(
        create_mock_http_error(mocker, data=None, status=400),
        "Failure in HTTP call 400 Client Error: Bad Request for url: https://ecm-east.us.code42.com/svc/api/v2/user/getbyusername.",
    )


@pytest.fixture
def change_org_response(mocker):
    return create_mock_response(mocker)


@pytest.fixture
def get_org_response(mocker):
    return create_mock_response(mocker, data=TEST_GET_ORG_RESPONSE)


@pytest.fixture
def get_org_success(cli_state, get_org_response):
    cli_state.sdk.orgs.get_by_uid.return_value = get_org_response


@pytest.fixture
def get_all_orgs_empty_success(mocker, cli_state):
    def get_all_orgs_empty_generator():
        yield create_mock_response(mocker, data=json.dumps(TEST_EMPTY_ORGS_RESPONSE))

    cli_state.sdk.orgs.get_all.return_value = get_all_orgs_empty_generator()


@pytest.fixture
def get_all_orgs_success(mocker, cli_state):
    def get_all_orgs_generator():
        yield create_mock_response(mocker, data=json.dumps(TEST_GET_ALL_ORGS_RESPONSE))

    cli_state.sdk.orgs.get_all.return_value = get_all_orgs_generator()


@pytest.fixture
def get_all_users_success(mocker, cli_state):
    def get_all_users_generator():
        yield create_mock_response(mocker, data=TEST_USERS_RESPONSE)

    cli_state.sdk.users.get_all.return_value = get_all_users_generator()


@pytest.fixture
def get_user_id_success(cli_state, get_users_response):
    """Get by username returns a list of users"""
    cli_state.sdk.users.get_by_username.return_value = get_users_response


@pytest.fixture
def get_user_uid_success(cli_state, get_user_response):
    """userriskprofile.get_by_username returns a single user"""
    cli_state.sdk.userriskprofile.get_by_username.return_value = get_user_response


@pytest.fixture
def get_user_uid_failure(cli_state, get_user_failure):
    cli_state.sdk.userriskprofile.get_by_username.side_effect = get_user_failure


@pytest.fixture
def get_user_id_failure(mocker, cli_state):
    cli_state.sdk.users.get_by_username.return_value = create_mock_response(
        mocker, data=TEST_EMPTY_USERS_RESPONSE
    )


@pytest.fixture
def get_custodian_failure(mocker, cli_state):
    def empty_custodian_list_generator():
        yield create_mock_response(mocker, data=TEST_EMPTY_CUSTODIANS_RESPONSE)

    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        empty_custodian_list_generator()
    )


@pytest.fixture
def get_matter_failure(mocker, cli_state):
    def empty_matter_list_generator():
        yield create_mock_response(mocker, data=TEST_EMPTY_MATTERS_RESPONSE)

    cli_state.sdk.legalhold.get_all_matters.return_value = empty_matter_list_generator()


@pytest.fixture
def get_all_matter_success(mocker, cli_state):
    def matter_list_generator():
        yield create_mock_response(mocker, data=TEST_MATTER_RESPONSE)

    cli_state.sdk.legalhold.get_all_matters.return_value = matter_list_generator()


@pytest.fixture
def get_all_custodian_success(mocker, cli_state):
    def custodian_list_generator():
        yield create_mock_response(mocker, data=TEST_CUSTODIANS_RESPONSE)

    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        custodian_list_generator()
    )


@pytest.fixture
def get_available_roles_success(cli_state, get_available_roles_response):
    cli_state.sdk.users.get_available_roles.return_value = get_available_roles_response


@pytest.fixture
def update_user_success(cli_state, update_user_response):
    cli_state.sdk.users.update_user.return_value = update_user_response


@pytest.fixture
def deactivate_user_success(mocker, cli_state):
    cli_state.sdk.users.deactivate.return_value = create_mock_response(mocker)


@pytest.fixture
def deactivate_user_legal_hold_failure(mocker, cli_state):
    cli_state.sdk.users.deactivate.side_effect = Py42ActiveLegalHoldError(
        create_mock_http_error(mocker, status=400), "user", TEST_USER_ID
    )


@pytest.fixture
def reactivate_user_success(mocker, cli_state):
    cli_state.sdk.users.deactivate.return_value = create_mock_response(mocker)


@pytest.fixture
def change_org_success(cli_state, change_org_response):
    cli_state.sdk.users.change_org_assignment.return_value = change_org_response


@pytest.fixture
def add_alias_success(mocker, cli_state):
    cli_state.sdk.detectionlists.add_user_cloud_alias.return_value = (
        create_mock_response(mocker)
    )


@pytest.fixture
def add_alias_limit_failure(mocker, cli_state):
    cli_state.sdk.userriskprofile.add_cloud_aliases.side_effect = (
        Py42CloudAliasLimitExceededError(create_mock_http_error(mocker))
    )


@pytest.fixture
def remove_alias_success(mocker, cli_state):
    cli_state.sdk.userriskprofile.delete_cloud_aliases.return_value = (
        create_mock_response(mocker)
    )


@pytest.fixture
def worker_stats_factory(mocker):
    return mocker.patch(f"{_NAMESPACE}.create_worker_stats")


@pytest.fixture
def worker_stats(mocker, worker_stats_factory):
    stats = mocker.MagicMock(spec=WorkerStats)
    worker_stats_factory.return_value = stats
    return stats


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
    role_name = "Customer Cloud Admin"
    runner.invoke(cli, ["users", "list", "--role-name", role_name], obj=cli_state)
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=None, org_uid=None, role_id="1234543", incRoles=False
    )


def test_list_users_calls_get_all_users_with_correct_parameters(
    runner, cli_state, get_all_users_success
):
    org_uid = "TEST_ORG_UID"
    runner.invoke(
        cli,
        ["users", "list", "--org-uid", org_uid, "--active", "--include-roles"],
        obj=cli_state,
    )
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=True, org_uid=org_uid, role_id=None, incRoles=True
    )


def test_list_users_when_given_inactive_uses_active_equals_false(
    runner, cli_state, get_available_roles_success, get_all_users_success
):
    runner.invoke(cli, ["users", "list", "--inactive"], obj=cli_state)
    cli_state.sdk.users.get_all.assert_called_once_with(
        active=False, org_uid=None, role_id=None, incRoles=False
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
        active=None, org_uid=None, role_id=None, incRoles=False
    )


def test_list_users_when_given_invalid_org_uid_raises_error(
    runner, cli_state, get_available_roles_success, custom_error
):
    invalid_org_uid = "invalid_org_uid"
    cli_state.sdk.users.get_all.side_effect = Py42OrgNotFoundError(
        custom_error, invalid_org_uid
    )
    result = runner.invoke(
        cli, ["users", "list", "--org-uid", invalid_org_uid], obj=cli_state
    )
    assert (
        f"Error: The organization with UID '{invalid_org_uid}' was not found."
        in result.output
    )


def test_list_legal_hold_flag_reports_none_for_users_not_on_legal_hold(
    runner,
    cli_state,
    get_all_users_success,
    get_custodian_failure,
    get_all_matter_success,
):
    result = runner.invoke(
        cli,
        ["users", "list", "--include-legal-hold-membership", "-f", "CSV"],
        obj=cli_state,
    )

    assert "Legal Hold #1,Legal Hold #2" not in result.output
    assert "123456789,987654321" not in result.output
    assert "legalHoldUid" not in result.output
    assert "test.username@example.com" in result.output


def test_list_legal_hold_flag_reports_none_if_no_matters_exist(
    runner, cli_state, get_all_users_success, get_custodian_failure, get_matter_failure
):
    result = runner.invoke(
        cli, ["users", "list", "--include-legal-hold-membership"], obj=cli_state
    )

    assert "Legal Hold #1,Legal Hold #2" not in result.output
    assert "123456789,987654321" not in result.output
    assert "legalHoldUid" not in result.output
    assert "test.username@example.com" in result.output


def test_list_legal_hold_values_not_included_for_legal_hold_user_if_legal_hold_flag_not_passed(
    runner,
    cli_state,
    get_all_users_success,
    get_all_custodian_success,
    get_all_matter_success,
):
    result = runner.invoke(cli, ["users", "list"], obj=cli_state)
    assert "Legal Hold #1,Legal Hold #2" not in result.output
    assert "123456789,987654321" not in result.output
    assert "test.username@example.com" in result.output


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


def test_list_prints_expected_data_if_include_roles(
    runner, cli_state, get_all_users_success
):
    result = runner.invoke(cli, ["users", "list", "--include-roles"], obj=cli_state)
    assert "roles" in result.output
    assert "Desktop User" in result.output


def test_show_calls_get_by_username_with_expected_params(runner, cli_state):
    runner.invoke(
        cli,
        ["users", "show", "test.username@example.com"],
        obj=cli_state,
    )
    cli_state.sdk.users.get_by_username.assert_called_once_with(
        "test.username@example.com", incRoles=True
    )


def test_show_prints_expected_data(runner, cli_state, get_users_response):
    cli_state.sdk.users.get_by_username.return_value = get_users_response
    result = runner.invoke(
        cli,
        ["users", "show", "test.username@example.com"],
        obj=cli_state,
    )
    assert "test.username@example.com" in result.output
    assert "911162111513111325" in result.output
    assert "Active" in result.output
    assert "44444444" in result.output
    assert "Desktop User" in result.output


def test_show_legal_hold_flag_reports_none_for_users_not_on_legal_hold(
    runner,
    cli_state,
    get_users_response,
    get_custodian_failure,
    get_all_matter_success,
):
    cli_state.sdk.users.get_by_username.return_value = get_users_response
    result = runner.invoke(
        cli,
        [
            "users",
            "show",
            "test.username@example.com",
            "--include-legal-hold-membership",
            "-f",
            "CSV",
        ],
        obj=cli_state,
    )

    assert "Legal Hold #1,Legal Hold #2" not in result.output
    assert "123456789,987654321" not in result.output
    assert "legalHoldUid" not in result.output
    assert "test.username@example.com" in result.output


def test_show_legal_hold_flag_reports_none_if_no_matters_exist(
    runner, cli_state, get_users_response, get_custodian_failure, get_matter_failure
):
    cli_state.sdk.users.get_by_username.return_value = get_users_response
    result = runner.invoke(
        cli,
        [
            "users",
            "show",
            "test.username@example.com",
            "--include-legal-hold-membership",
        ],
        obj=cli_state,
    )

    assert "Legal Hold #1,Legal Hold #2" not in result.output
    assert "123456789,987654321" not in result.output
    assert "legalHoldUid" not in result.output
    assert "test.username@example.com" in result.output


def test_show_legal_hold_values_not_included_for_legal_hold_user_if_legal_hold_flag_not_passed(
    runner,
    cli_state,
    get_users_response,
    get_all_custodian_success,
    get_all_matter_success,
):
    cli_state.sdk.users.get_by_username.return_value = get_users_response
    result = runner.invoke(
        cli, ["users", "show", "test.username@example.com"], obj=cli_state
    )
    assert "Legal Hold #1,Legal Hold #2" not in result.output
    assert "123456789,987654321" not in result.output
    assert "test.username@example.com" in result.output


def test_show_include_legal_hold_membership_merges_in_and_concats_legal_hold_info(
    runner,
    cli_state,
    get_users_response,
    get_all_custodian_success,
    get_all_matter_success,
):
    cli_state.sdk.users.get_by_username.return_value = get_users_response
    result = runner.invoke(
        cli,
        [
            "users",
            "show",
            "test.username@example.com",
            "--include-legal-hold-membership",
        ],
        obj=cli_state,
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
    assert (
        "User 'not_a_username@example.com' does not exist or you do not have permission to view them."
        in result.output
    )


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
    assert (
        "User 'not_a_username@example.com' does not exist or you do not have permission to view them."
        in result.output
    )


def test_update_user_calls_update_user_with_correct_parameters_when_only_some_are_passed(
    runner, cli_state, update_user_success
):
    command = ["users", "update", "--user-id", "12345", "--email", "test_email"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.users.update_user.assert_called_once_with(
        "12345",
        username=None,
        email="test_email",
        password=None,
        first_name=None,
        last_name=None,
        notes=None,
        archive_size_quota_bytes=None,
    )


def test_update_user_calls_update_user_with_correct_parameters_when_all_are_passed(
    runner, cli_state, update_user_success
):
    command = [
        "users",
        "update",
        "--user-id",
        "12345",
        "--email",
        "test_email",
        "--username",
        "test_username",
        "--password",
        "test_password",
        "--first-name",
        "test_fname",
        "--last-name",
        "test_lname",
        "--notes",
        "test notes",
        "--archive-size-quota",
        "123456",
    ]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.users.update_user.assert_called_once_with(
        "12345",
        username="test_username",
        email="test_email",
        password="test_password",
        first_name="test_fname",
        last_name="test_lname",
        notes="test notes",
        archive_size_quota_bytes="123456",
    )


def test_update_when_py42_raises_invalid_email_outputs_error_message(
    mocker, runner, cli_state, update_user_success
):
    test_email = "test_email"
    mock_http_error = create_mock_http_error(mocker, status=500)
    cli_state.sdk.users.update_user.side_effect = Py42InvalidEmailError(
        test_email, mock_http_error
    )
    command = ["users", "update", "--user-id", "12345", "--email", test_email]
    result = runner.invoke(cli, command, obj=cli_state)
    assert "Error: 'test_email' is not a valid email." in result.output


def test_update_when_py42_raises_invalid_username_outputs_error_message(
    mocker, runner, cli_state, update_user_success
):
    mock_http_error = create_mock_http_error(mocker, status=500)
    cli_state.sdk.users.update_user.side_effect = Py42InvalidUsernameError(
        mock_http_error
    )
    command = ["users", "update", "--user-id", "12345", "--username", "test_username"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert "Error: Invalid username." in result.output


def test_update_when_py42_raises_invalid_password_outputs_error_message(
    mocker, runner, cli_state, update_user_success
):
    mock_http_error = create_mock_http_error(mocker, status=500)
    cli_state.sdk.users.update_user.side_effect = Py42InvalidPasswordError(
        mock_http_error
    )
    command = ["users", "update", "--user-id", "12345", "--password", "test_password"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert "Error: Invalid password." in result.output


def test_deactivate_calls_deactivate_with_correct_parameters(
    runner, cli_state, get_user_id_success, deactivate_user_success
):
    command = ["users", "deactivate", "test@example.com"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.users.deactivate.assert_called_once_with(TEST_USER_ID)


def test_deactivate_when_user_on_legal_hold_outputs_expected_error_text(
    runner, cli_state, get_user_id_success, deactivate_user_legal_hold_failure
):
    command = ["users", "deactivate", "test@example.com"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert (
        "Error: Cannot deactivate the user with ID 1234 as the user is involved in a legal hold matter."
        in result.output
    )


def test_reactivate_calls_reactivate_with_correct_parameters(
    runner, cli_state, get_user_id_success, deactivate_user_success
):
    command = ["users", "reactivate", "test@example.com"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.users.reactivate.assert_called_once_with(TEST_USER_ID)


def test_bulk_update_uses_expected_arguments_when_only_some_are_passed(
    runner, mocker, cli_state
):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_update.csv", "w") as csv:
            csv.writelines(
                [
                    "user_id,username,email,password,first_name,last_name,notes,archive_size_quota\n",
                    "12345,,test_email,,,,,\n",
                ]
            )
        runner.invoke(
            cli, ["users", "bulk", "update", "test_bulk_update.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "user_id": "12345",
            "username": "",
            "email": "test_email",
            "password": "",
            "first_name": "",
            "last_name": "",
            "notes": "",
            "archive_size_quota": "",
            "updated": "False",
        }
    ]


def test_bulk_update_uses_expected_arguments_when_all_are_passed(
    runner, mocker, cli_state
):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_update.csv", "w") as csv:
            csv.writelines(
                [
                    "user_id,username,email,password,first_name,last_name,notes,archive_size_quota\n",
                    "12345,test_username,test_email,test_pword,test_fname,test_lname,test notes,4321\n",
                ]
            )
        runner.invoke(
            cli, ["users", "bulk", "update", "test_bulk_update.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "user_id": "12345",
            "username": "test_username",
            "email": "test_email",
            "password": "test_pword",
            "first_name": "test_fname",
            "last_name": "test_lname",
            "notes": "test notes",
            "archive_size_quota": "4321",
            "updated": "False",
        }
    ]


def test_bulk_update_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_update.csv", "w") as csv:
            csv.writelines(
                [
                    "user_id,username,email,password,first_name,last_name,notes,archive_size_quota\n",
                    "\n",
                    "12345,test_username,test_email,test_pword,test_fname,test_lname,test notes,4321\n",
                    "\n",
                ]
            )
        runner.invoke(
            cli, ["users", "bulk", "update", "test_bulk_update.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "user_id": "12345",
            "username": "test_username",
            "email": "test_email",
            "password": "test_pword",
            "first_name": "test_fname",
            "last_name": "test_lname",
            "notes": "test notes",
            "archive_size_quota": "4321",
            "updated": "False",
        }
    ]


def test_bulk_update_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats
):
    lines = [
        "user_id,username,email,password,first_name,last_name,notes,archive_size_quota\n",
        "12345,test_username,test_email,test_pword,test_fname,test_lname,test notes,4321\n",
    ]

    def _update(user_id, *args, **kwargs):
        if user_id == "12345":
            raise Exception("TEST")
        return create_mock_response(mocker, data=TEST_USERS_RESPONSE)

    cli_state.sdk.users.update_user.side_effect = _update
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_update.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["users", "bulk", "update", "test_bulk_update.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(
        user_id="12345",
        username="test",
        email="test",
        password="test",
        first_name="test",
        last_name="test",
        notes="test",
        archive_size_quota="test",
    )
    handler(
        user_id="not 12345",
        username="test",
        email="test",
        password="test",
        first_name="test",
        last_name="test",
        notes="test",
        archive_size_quota="test",
    )
    assert worker_stats.increment_total_errors.call_count == 1


def test_move_calls_change_org_assignment_with_correct_parameters(
    runner, cli_state, change_org_success, get_user_id_success, get_org_success
):
    command = [
        "users",
        "move",
        "--username",
        TEST_USERNAME,
        "--org-id",
        "1007744453331222111",
    ]
    runner.invoke(cli, command, obj=cli_state)
    expected_org_id = TEST_GET_ORG_RESPONSE["orgId"]
    cli_state.sdk.users.change_org_assignment.assert_called_once_with(
        user_id=TEST_USER_ID, org_id=expected_org_id
    )


def test_bulk_move_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_move.csv", "w") as csv:
            csv.writelines(["username,org_id\n", f"{TEST_USERNAME},4321\n"])
        runner.invoke(
            cli, ["users", "bulk", "move", "test_bulk_move.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "org_id": "4321", "moved": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_move_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_move.csv", "w") as csv:
            csv.writelines(["username,org_id\n\n\n", f"{TEST_USERNAME},4321\n\n\n"])
        runner.invoke(
            cli, ["users", "bulk", "move", "test_bulk_move.csv"], obj=cli_state
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "org_id": "4321", "moved": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_move_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats, get_users_response
):
    lines = ["username,org_id\n", f"{TEST_USERNAME},4321\n"]

    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")
        return get_users_response

    cli_state.sdk.users.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_move.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["users", "bulk", "move", "test_bulk_move.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(username="test@example.com", org_id="test")
    handler(username="not.test@example.com", org_id="test")
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_move_uses_handle_than_when_called_and_row_has_missing_username_errors_at_row(
    runner, mocker, cli_state, worker_stats
):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    lines = ["username,org_id\n", ",123\n"]  # Missing username
    with runner.isolated_filesystem():
        with open("test_bulk_move.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli, ["users", "bulk", "move", "test_bulk_move.csv"], obj=cli_state
        )

    handler = bulk_processor.call_args[0][0]
    handler(username=None, org_id="123")
    assert worker_stats.increment_total_errors.call_count == 1
    # Ensure it does not try to get the username for the None user.
    assert not cli_state.sdk.users.get_by_username.call_count


def test_bulk_deactivate_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(["username\n", f"{TEST_USERNAME}\n"])
        runner.invoke(
            cli,
            ["users", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "deactivated": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_deactivate_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(["username\n\n\n", f"{TEST_USERNAME}\n\n\n"])
        runner.invoke(
            cli,
            ["users", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "deactivated": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_deactivate_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats, get_users_response
):
    lines = ["username\n", f"{TEST_USERNAME}\n"]

    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")
        return get_users_response

    cli_state.sdk.users.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["users", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(username="test@example.com")
    handler(username="not.test@example.com")
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_reactivate_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(["username\n", f"{TEST_USERNAME}\n"])
        runner.invoke(
            cli,
            ["users", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "reactivated": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_reactivate_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(["username\n\n\n", f"{TEST_USERNAME}\n\n\n"])
        runner.invoke(
            cli,
            ["users", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "reactivated": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_reactivate_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats, get_users_response
):
    lines = ["username\n", f"{TEST_USERNAME}\n"]

    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")

        return get_users_response

    cli_state.sdk.users.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["users", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(username="test@example.com")
    handler(username="not.test@example.com")
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_add_roles_uses_expected_arguments(runner, mocker, cli_state_with_user):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_add_roles.csv", "w") as csv:
            csv.writelines(
                ["username,role_name\n", f"{TEST_USERNAME},{TEST_ROLE_NAME}\n"]
            )
        command = ["users", "bulk", "add-roles", "test_bulk_add_roles.csv"]
        runner.invoke(
            cli,
            command,
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "role_name": TEST_ROLE_NAME, "role added": "False"},
    ]
    bulk_processor.assert_called_once()


def test_bulk_add_roles_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_add_roles.csv", "w") as csv:
            csv.writelines(
                ["username,role_name\n\n\n", f"{TEST_USERNAME},{TEST_ROLE_NAME}\n\n\n"]
            )
        runner.invoke(
            cli,
            ["users", "bulk", "add-roles", "test_bulk_add_roles.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "role_name": TEST_ROLE_NAME, "role added": "False"},
    ]
    bulk_processor.assert_called_once()


def test_bulk_add_roles_uses_handler_that_when_encounters_error_increments_total_errors(
    runner,
    mocker,
    cli_state,
    worker_stats,
    get_users_response,
    get_available_roles_success,
):
    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")
        return get_users_response

    cli_state.sdk.users.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_add_roles.csv", "w") as csv:
            csv.writelines(
                ["username,role_name\n", f"{TEST_USERNAME},{TEST_ROLE_NAME}\n"]
            )

        runner.invoke(
            cli,
            ["users", "bulk", "add-roles", "test_bulk_add_roles.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]

    handler(
        username="test@example.com",
        role_name=TEST_ROLE_NAME,
    )
    handler(username="not.test@example.com", role_name=TEST_ROLE_NAME)
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_remove_roles_uses_expected_arguments(runner, mocker, cli_state_with_user):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_remove_roles.csv", "w") as csv:
            csv.writelines(
                ["username,role_name\n", f"{TEST_USERNAME},{TEST_ROLE_NAME}\n"]
            )
        command = ["users", "bulk", "remove-roles", "test_bulk_remove_roles.csv"]
        runner.invoke(
            cli,
            command,
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "username": TEST_USERNAME,
            "role_name": TEST_ROLE_NAME,
            "role removed": "False",
        },
    ]
    bulk_processor.assert_called_once()


def test_bulk_remove_roles_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_remove_roles.csv", "w") as csv:
            csv.writelines(
                ["username,role_name\n\n\n", f"{TEST_USERNAME},{TEST_ROLE_NAME}\n\n\n"]
            )
        runner.invoke(
            cli,
            ["users", "bulk", "remove-roles", "test_bulk_remove_roles.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "username": TEST_USERNAME,
            "role_name": TEST_ROLE_NAME,
            "role removed": "False",
        },
    ]
    bulk_processor.assert_called_once()


def test_bulk_remove_roles_uses_handler_that_when_encounters_error_increments_total_errors(
    runner,
    mocker,
    cli_state,
    worker_stats,
    get_users_response,
    get_available_roles_success,
):
    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")

        return get_users_response

    cli_state.sdk.users.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_remove_roles.csv", "w") as csv:
            csv.writelines(
                ["username,role_name\n", f"{TEST_USERNAME},{TEST_ROLE_NAME}\n"]
            )

        runner.invoke(
            cli,
            ["users", "bulk", "remove-roles", "test_bulk_remove_roles.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(
        username="test@example.com",
        role_name=TEST_ROLE_NAME,
    )
    handler(username="not.test@example.com", role_name=TEST_ROLE_NAME)
    assert worker_stats.increment_total_errors.call_count == 1


def test_orgs_list_calls_orgs_get_all_with_expected_params(runner, cli_state):
    runner.invoke(cli, ["users", "orgs", "list"], obj=cli_state)
    assert cli_state.sdk.orgs.get_all.call_count == 1


def test_orgs_list_prints_no_results_if_no_orgs_found(
    runner, cli_state, get_all_orgs_empty_success
):
    result = runner.invoke(cli, ["users", "orgs", "list"], obj=cli_state)
    assert "No orgs found." in result.output


def test_orgs_list_prints_expected_data(runner, cli_state, get_all_orgs_success):
    result = runner.invoke(cli, ["users", "orgs", "list"], obj=cli_state)
    assert "9087" in result.output
    assert "1007759454961904673" in result.output
    assert "19may" in result.output
    assert "Active" in result.output
    assert "2689" in result.output
    assert "890854247383106706" in result.output
    assert "ENTERPRISE" in result.output
    assert "BASIC" in result.output
    assert "2021-05-19T10:10:43.459Z" in result.output
    assert "{'maxSeats': None, 'maxBytes': None}" in result.output


def test_orgs_list_prints_all_data_fields_when_not_table_format(
    runner, cli_state, get_all_orgs_success
):
    result = runner.invoke(cli, ["users", "orgs", "list", "-f", "JSON"], obj=cli_state)
    for k, _v in TEST_GET_ORG_RESPONSE.items():
        assert k in result.output
    assert "9087" in result.output
    assert "1007759454961904673" in result.output
    assert "19may" in result.output
    assert "Active" in result.output
    assert "2689" in result.output
    assert "890854247383106706" in result.output
    assert "ENTERPRISE" in result.output
    assert "BASIC" in result.output
    assert "2021-05-19T10:10:43.459Z" in result.output
    assert '"maxSeats": null' in result.output
    assert '"maxSeats": null' in result.output


def test_orgs_show_calls_orgs_get_by_uid_with_expected_params(
    runner,
    cli_state,
):
    runner.invoke(cli, ["users", "orgs", "show", TEST_ORG_UID], obj=cli_state)
    cli_state.sdk.orgs.get_by_uid.assert_called_once_with(TEST_ORG_UID)


def test_orgs_show_exits_and_returns_error_if_uid_arg_not_provided(runner, cli_state):
    result = runner.invoke(cli, ["users", "orgs", "show"], obj=cli_state)
    assert result.exit_code == 2
    assert "Error: Missing argument 'ORG_UID'." in result.output


def test_orgs_show_prints_expected_data(
    runner,
    cli_state,
    get_org_success,
):
    result = runner.invoke(cli, ["users", "orgs", "show", TEST_ORG_UID], obj=cli_state)
    assert "9087" in result.output
    assert "1007759454961904673" in result.output
    assert "19may" in result.output
    assert "Active" in result.output
    assert "2689" in result.output
    assert "890854247383106706" in result.output
    assert "ENTERPRISE" in result.output
    assert "BASIC" in result.output
    assert "2021-05-19T10:10:43.459Z" in result.output
    assert "{'maxSeats': None, 'maxBytes': None}" in result.output


def test_orgs_show_prints_all_data_fields_when_not_table_format(
    runner,
    cli_state,
    get_org_success,
):
    result = runner.invoke(
        cli, ["users", "orgs", "show", TEST_ORG_UID, "-f", "JSON"], obj=cli_state
    )
    for k, _v in TEST_GET_ORG_RESPONSE.items():
        assert k in result.output
    assert "9087" in result.output
    assert "1007759454961904673" in result.output
    assert "19may" in result.output
    assert "Active" in result.output
    assert "2689" in result.output
    assert "890854247383106706" in result.output
    assert "ENTERPRISE" in result.output
    assert "BASIC" in result.output
    assert "2021-05-19T10:10:43.459Z" in result.output
    assert '"maxSeats": null' in result.output
    assert '"maxSeats": null' in result.output


def test_orgs_show_when_invalid_org_uid_raises_error(runner, cli_state, custom_error):
    cli_state.sdk.orgs.get_by_uid.side_effect = Py42NotFoundError(custom_error)
    result = runner.invoke(cli, ["users", "orgs", "show", TEST_ORG_UID], obj=cli_state)
    assert result.exit_code == 1
    assert f"Invalid org UID {TEST_ORG_UID}." in result.output


def test_list_aliases_calls_get_user_with_expected_parameters(runner, cli_state):
    username = "alias@example"
    command = ["users", "list-aliases", username]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.userriskprofile.get_by_username.assert_called_once_with("alias@example")


def test_list_aliases_prints_no_aliases_found_when_empty_list(
    runner, cli_state, mocker
):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(
        mocker, data={"cloudAliases": []}
    )
    username = "alias@example"
    command = ["users", "list-aliases", username]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 0
    assert f"No cloud aliases for user '{username}' found" in result.output


def test_list_aliases_prints_expected_data(runner, cli_state, get_user_uid_success):
    result = runner.invoke(
        cli, ["users", "list-aliases", "alias@example.com"], obj=cli_state
    )
    assert result.exit_code == 0
    assert "['Sample.User1@samplecase.com', 'Sample.User1@gmail.com']" in result.output


def test_list_aliases_raises_error_when_user_does_not_exist(
    runner, cli_state, get_user_uid_failure
):
    username = "fake@notreal.com"
    command = ["users", "list-aliases", username]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert (
        f"User '{username}' does not exist or you do not have permission to view them."
        in result.output
    )


def test_add_cloud_alias_calls_add_cloud_alias_with_correct_parameters(
    runner, cli_state, get_user_uid_success, add_alias_success
):
    command = ["users", "add-alias", "test@example.com", "alias@example.com"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.userriskprofile.add_cloud_aliases.assert_called_once_with(
        TEST_USER_UID, "alias@example.com"
    )


def test_add_alias_raises_error_when_user_does_not_exist(
    runner, cli_state, get_user_uid_failure
):
    username = "fake@notreal.com"
    command = ["users", "add-alias", username, "alias@example.com"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert (
        f"User '{username}' does not exist or you do not have permission to view them."
        in result.output
    )


def test_add_alias_raises_error_when_alias_is_too_long(runner, cli_state):
    command = [
        "users",
        "add-alias",
        "fake@notreal.com",
        "alias-is-too-long-its-very-long-for-real-more-than-50-characters@example.com",
    ]
    cli_state.sdk.userriskprofile.add_cloud_aliases.side_effect = (
        Py42CloudAliasCharacterLimitExceededError
    )
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert "Cloud alias character limit exceeded" in result.output


def test_add_alias_raises_error_when_user_has_two_aliases(
    runner, cli_state, add_alias_limit_failure
):
    command = [
        "users",
        "add-alias",
        "fake@notreal.com",
        "second_alias",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert (
        "Error: Cloud alias limit exceeded. A max of 2 cloud aliases are allowed."
        in result.output
    )


def test_remove_cloud_alias_calls_remove_cloud_alias_with_correct_parameters(
    runner, cli_state, get_user_uid_success, remove_alias_success
):
    command = ["users", "remove-alias", "test@example.com", "alias@example.com"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.userriskprofile.delete_cloud_aliases.assert_called_once_with(
        TEST_USER_UID, "alias@example.com"
    )


def test_remove_alias_raises_error_when_user_does_not_exist(
    runner, cli_state, get_user_uid_failure
):
    username = "fake@notreal.com"
    command = ["users", "remove-alias", username, "alias@example.com"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert (
        f"User '{username}' does not exist or you do not have permission to view them."
        in result.output
    )


def test_bulk_add_alias_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_add_alias.csv", "w") as csv:
            csv.writelines(["username,alias\n", f"{TEST_USERNAME},{TEST_ALIAS}\n"])
        runner.invoke(
            cli,
            ["users", "bulk", "add-alias", "test_add_alias.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "alias": TEST_ALIAS, "alias added": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_add_alias_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_add_alias.csv", "w") as csv:
            csv.writelines(
                ["username,alias\n\n\n", f"{TEST_USERNAME},{TEST_ALIAS}\n\n\n"]
            )
        runner.invoke(
            cli,
            ["users", "bulk", "add-alias", "test_add_alias.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "alias": TEST_ALIAS, "alias added": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_add_alias_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats, get_user_response
):
    lines = ["username,alias\n", f"{TEST_USERNAME},{TEST_ALIAS}\n"]

    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")
        return get_user_response

    cli_state.sdk.userriskprofile.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_add_alias.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["users", "bulk", "add-alias", "test_add_alias.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(username="test@example.com", alias=TEST_ALIAS)
    handler(username="not.test@example.com", alias=TEST_ALIAS)
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_remove_alias_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove_alias.csv", "w") as csv:
            csv.writelines(["username,alias\n", f"{TEST_USERNAME},{TEST_ALIAS}\n"])
        runner.invoke(
            cli,
            ["users", "bulk", "remove-alias", "test_remove_alias.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "alias": TEST_ALIAS, "alias removed": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_remove_alias_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove_alias.csv", "w") as csv:
            csv.writelines(
                ["username,alias\n\n\n", f"{TEST_USERNAME},{TEST_ALIAS}\n\n\n"]
            )
        runner.invoke(
            cli,
            ["users", "bulk", "remove-alias", "test_remove_alias.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"username": TEST_USERNAME, "alias": TEST_ALIAS, "alias removed": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_remove_alias_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats, get_user_response
):
    lines = ["username,alias\n", f"{TEST_USERNAME},{TEST_ALIAS}\n"]

    def _get(username, *args, **kwargs):
        if username == "test@example.com":
            raise Exception("TEST")
        return get_user_response

    cli_state.sdk.userriskprofile.get_by_username.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove_alias.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["users", "bulk", "remove-alias", "test_remove_alias.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(username="test@example.com", alias=TEST_ALIAS)
    handler(username="not.test@example.com", alias=TEST_ALIAS)
    assert worker_stats.increment_total_errors.call_count == 1


def test_update_start_date_without_date_arg_or_clear_option_raises_cli_error(runner, cli_state):
    res = runner.invoke(cli, ["users", "update-start-date", "test@example.com"], obj=cli_state)
    assert res.exit_code == 1
    assert "Must supply DATE argument if --clear is not used." in res.output


def test_update_start_date_with_date_makes_expected_call(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    res = runner.invoke(cli, ["users", "update-start-date", "test@example.com", "2020-10-10"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, start_date=datetime.datetime(2020, 10, 10))


def test_update_start_date_with_clear_option_clears_date(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    res = runner.invoke(cli, ["users", "update-start-date", "test@example.com", "--clear"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, start_date="")


def test_update_departure_date_without_date_arg_or_clear_option_raises_cli_error(runner, cli_state):
    res = runner.invoke(cli, ["users", "update-departure-date", "test@example.com"], obj=cli_state)
    assert res.exit_code == 1
    assert "Must supply DATE argument if --clear is not used." in res.output


def test_update_departure_date_with_clear_option_clears_date(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    res = runner.invoke(cli, ["users", "update-departure-date", "test@example.com", "--clear"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, end_date="")


def test_update_departure_date_with_date_makes_expected_call(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    res = runner.invoke(cli, ["users", "update-departure-date", "test@example.com", "2020-10-10"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, end_date=datetime.datetime(2020, 10, 10))


def test_update_notes_without_note_arg_or_clear_option_raises_cli_error(runner, cli_state):
    res = runner.invoke(cli, ["users", "update-risk-profile-notes", "test@example.com"], obj=cli_state)
    assert res.exit_code == 1
    assert "Must supply NOTE argument if --clear is not used." in res.output


def test_update_notes_with_clear_option_clears_date(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    res = runner.invoke(cli, ["users", "update-risk-profile-notes", "test@example.com", "--clear"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, notes="")


def test_update_notes_with_note_makes_expected_call(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    res = runner.invoke(cli, ["users", "update-risk-profile-notes", "test@example.com", "new note"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, notes="new note")


def test_update_notes_with_append_option_appends_note_value(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234, "notes": "existing note"})
    res = runner.invoke(cli, ["users", "update-risk-profile-notes", "test@example.com", "--append", "new note"], obj=cli_state)
    assert res.exit_code == 0
    cli_state.sdk.userriskprofile.update.assert_called_once_with(1234, notes="existing note\n\nnew note")


def test_bulk_update_risk_profile_makes_expected_calls(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={"userId": 1234})
    with runner.isolated_filesystem():
        with open("csv", "w") as file:
            file.write("username,start_date,end_date,notes\ntest@example.com,2020-10-10,2022-10-10,new note\n")
        res = runner.invoke(cli, ["users", "bulk", "update-risk-profile", "csv"], obj=cli_state)
        assert res.exit_code == 0
        cli_state.sdk.userriskprofile.update.assert_called_once_with(
            1234,
            start_date="2020-10-10",
            end_date="2022-10-10",
            notes="new note"
        )
    
    
def test_bulk_update_risk_profile_with_append_note_option_appends_note(mocker, runner, cli_state):
    cli_state.sdk.userriskprofile.get_by_username.return_value = create_mock_response(mocker, data={
        "userId": 1234, "notes":"existing note"})
    with runner.isolated_filesystem():
        with open("csv", "w") as file:
            file.write(
                "username,start_date,end_date,notes\ntest@example.com,2020-10-10,2022-10-10,new note\n")
        res = runner.invoke(cli, ["users", "bulk", "update-risk-profile", "--append-notes", "csv"], obj=cli_state)
        assert res.exit_code == 0
        cli_state.sdk.userriskprofile.update.assert_called_once_with(
            1234,
            start_date="2020-10-10",
            end_date="2022-10-10",
            notes="existing note\n\nnew note"
        )
