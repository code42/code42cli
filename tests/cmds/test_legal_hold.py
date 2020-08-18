import pytest
from py42.exceptions import Py42BadRequestError
from py42.response import Py42Response
from requests import HTTPError
from requests import Response

from code42cli import PRODUCT_NAME
from code42cli.cmds.legal_hold import _check_matter_is_accessible
from code42cli.main import cli

_NAMESPACE = "{}.cmds.legal_hold".format(PRODUCT_NAME)

TEST_MATTER_ID = "99999"
TEST_LEGAL_HOLD_MEMBERSHIP_UID = "88888"
TEST_LEGAL_HOLD_MEMBERSHIP_UID_2 = "77777"
ACTIVE_TEST_USERNAME = "user@example.com"
ACTIVE_TEST_USER_ID = "12345"
INACTIVE_TEST_USERNAME = "inactive@example.com"
INACTIVE_TEST_USER_ID = "54321"

TEST_POLICY_UID = "66666"

TEST_MATTER_RESULT = {
    "legalHoldUid": TEST_LEGAL_HOLD_MEMBERSHIP_UID,
    "name": "Test_Matter",
    "description": "",
    "active": True,
    "creationDate": "2020-01-01T00:00:00.000-06:00",
    "creator": {"userUid": "942564422882759874", "username": "legal_admin@example.com"},
    "holdPolicyUid": TEST_POLICY_UID,
}

ACTIVE_LEGAL_HOLD_MEMBERSHIP = {
    "legalHoldMembershipUid": TEST_LEGAL_HOLD_MEMBERSHIP_UID,
    "user": {"userUid": ACTIVE_TEST_USER_ID, "username": ACTIVE_TEST_USERNAME},
    "active": True,
}
INACTIVE_LEGAL_HOLD_MEMBERSHIP = {
    "legalHoldMembershipUid": TEST_LEGAL_HOLD_MEMBERSHIP_UID_2,
    "user": {"userUid": INACTIVE_TEST_USER_ID, "username": INACTIVE_TEST_USERNAME},
    "active": False,
}


EMPTY_LEGAL_HOLD_MEMBERSHIPS_RESULT = [{"legalHoldMemberships": []}]
ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT = [
    {"legalHoldMemberships": [ACTIVE_LEGAL_HOLD_MEMBERSHIP]}
]
ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT = [
    {
        "legalHoldMemberships": [
            ACTIVE_LEGAL_HOLD_MEMBERSHIP,
            INACTIVE_LEGAL_HOLD_MEMBERSHIP,
        ]
    }
]
INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT = [
    {"legalHoldMemberships": [INACTIVE_LEGAL_HOLD_MEMBERSHIP]}
]

TEST_PRESERVATION_POLICY_UID = "1010101010"
TEST_PRESERVATION_POLICY_JSON = '{{"creationDate": "2020-01-01","legalHoldPolicyUid": {}}}'.format(
    TEST_PRESERVATION_POLICY_UID
)

TEST_LEGAL_HOLD_LIST = [
    {
        "legalHolds": [
            {
                "legalHoldUid": "932880202064992021",
                "name": "test",
                "description": "",
                "active": True,
                "creationDate": "2019-12-19T20:32:10.763Z",
                "lastModified": "2019-12-19T20:32:10.781Z",
                "creator": {
                    "userUid": "921286907298179098",
                    "username": "test@test.test",
                    "email": "test@test.test",
                },
                "holdPolicyUid": "901109555892625150",
                "creator_username": "test@test.test",
            },
        ],
    }
]

TEST_LEGAL_HOLD_EMPTY_LIST = [{"legalHolds": []}]


@pytest.fixture
def preservation_policy_response(mocker):
    response = mocker.MagicMock(spec=Response)
    response.text = TEST_PRESERVATION_POLICY_JSON
    return Py42Response(response)


@pytest.fixture
def get_user_id_success(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {
        "users": [{"userUid": ACTIVE_TEST_USER_ID}]
    }


@pytest.fixture
def get_user_id_failure(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {"users": []}


@pytest.fixture
def check_matter_accessible_success(cli_state):
    cli_state.sdk.legalhold.get_matter_by_uid.return_value = TEST_MATTER_RESULT


@pytest.fixture
def check_matter_accessible_failure(cli_state):
    cli_state.sdk.legalhold.get_matter_by_uid.side_effect = Py42BadRequestError(
        HTTPError()
    )


@pytest.fixture
def user_already_added_response(mocker):
    mock_response = mocker.MagicMock(spec=Response)
    mock_response.text = "USER_ALREADY_IN_HOLD"
    http_error = HTTPError()
    http_error.response = mock_response
    return Py42BadRequestError(http_error)


def test_add_user_raises_user_already_added_error_when_user_already_on_hold(
    runner, cli_state, user_already_added_response
):

    cli_state.sdk.legalhold.add_to_matter.side_effect = user_already_added_response
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "add-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert "'{}' is already on the legal hold matter id={}".format(
        ACTIVE_TEST_USERNAME, TEST_MATTER_ID
    )


def test_add_user_raises_legalhold_not_found_error_if_matter_inaccessible(
    runner, cli_state, check_matter_accessible_failure, get_user_id_success
):
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "add-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert "Matter with id={} either does not exist or your profile does not have permission to view it.".format(
        TEST_MATTER_ID
    )


def test_add_user_adds_user_to_hold_if_user_and_matter_exist(
    runner, cli_state, check_matter_accessible_success, get_user_id_success
):
    runner.invoke(
        cli,
        [
            "legal-hold",
            "add-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    cli_state.sdk.legalhold.add_to_matter.assert_called_once_with(
        ACTIVE_TEST_USER_ID, TEST_MATTER_ID
    )


def test_remove_user_raises_legalhold_not_found_error_if_matter_inaccessible(
    runner, cli_state, check_matter_accessible_failure, get_user_id_success
):
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "remove-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        "Matter with id={} either does not exist or your profile does not have "
        "permission to view it.".format(TEST_MATTER_ID)
    )


def test_remove_user_raises_user_not_in_matter_error_if_user_not_active_in_matter(
    runner, cli_state, check_matter_accessible_success, get_user_id_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        EMPTY_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "remove-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert "User '{}' is not an active member of legal hold matter '{}'".format(
        ACTIVE_TEST_USERNAME, TEST_MATTER_ID
    )


def test_remove_user_removes_user_if_user_in_matter(
    runner, cli_state, check_matter_accessible_success, get_user_id_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )

    membership_uid = ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT[0]["legalHoldMemberships"][0][
        "legalHoldMembershipUid"
    ]
    runner.invoke(
        cli,
        [
            "legal-hold",
            "remove-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    cli_state.sdk.legalhold.remove_from_matter.assert_called_with(membership_uid)


def test_matter_accessible_check_only_makes_one_http_call_when_called_multiple_times_with_same_matter_id(
    sdk, check_matter_accessible_success
):
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    assert sdk.legalhold.get_matter_by_uid.call_count == 1


def test_show_matter_prints_active_and_inactive_results_when_include_inactive_flag_set(
    runner, cli_state, check_matter_accessible_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME in result.output


def test_show_matter_prints_active_results_only(
    runner, cli_state, check_matter_accessible_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME not in result.output


def test_show_matter_prints_no_active_members_when_no_membership(
    runner, cli_state, check_matter_accessible_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        EMPTY_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME not in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_no_inactive_members_when_no_inactive_membership(
    runner, cli_state, check_matter_accessible_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME not in result.output
    assert "No inactive matter members." in result.output


def test_show_matter_prints_no_active_members_when_no_active_membership(
    runner, cli_state, check_matter_accessible_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_no_active_members_when_no_active_membership_and_inactive_membership_included(
    runner, cli_state, check_matter_accessible_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_preservation_policy_when_include_policy_flag_set(
    runner, cli_state, check_matter_accessible_success, preservation_policy_response
):
    cli_state.sdk.legalhold.get_policy_by_uid.return_value = (
        preservation_policy_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-policy"], obj=cli_state
    )
    assert TEST_PRESERVATION_POLICY_UID in result.output


def test_show_matter_does_not_print_preservation_policy(
    runner, cli_state, check_matter_accessible_success, preservation_policy_response
):
    cli_state.sdk.legalhold.get_policy_by_uid.return_value = (
        preservation_policy_response
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert TEST_PRESERVATION_POLICY_UID not in result.output


def test_add_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    with runner.isolated_filesystem():
        with open("test_add.csv", "w") as csv:
            csv.writelines(["matter_id,username\n", "test,value\n"])
        runner.invoke(cli, ["legal-hold", "bulk", "add", "test_add.csv"], obj=cli_state)
    assert bulk_processor.call_args[0][1] == [
        {"matter_id": "test", "username": "value"}
    ]


def test_remove_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["matter_id,username\n", "test,value\n"])
        runner.invoke(
            cli, ["legal-hold", "bulk", "remove", "test_remove.csv"], obj=cli_state
        )
        assert bulk_processor.call_args[0][1] == [
            {"matter_id": "test", "username": "value"}
        ]


def test_list_with_format_option_returns_expected_format(runner, cli_state):
    cli_state.sdk.legalhold.get_all_matters.return_value = TEST_LEGAL_HOLD_LIST

    result = runner.invoke(cli, ["legal-hold", "list", "-f", "csv"], obj=cli_state)
    assert (
        "legalHoldUid,name,description,active,creationDate,lastModified,creator,holdPolicyUid,creator_username"
        in result.output
    )
    assert "932880202064992021" in result.output


def test_list_with_format_option_returns_no_response_when_response_is_empty(
    runner, cli_state
):
    cli_state.sdk.legalhold.get_all_matters.return_value = TEST_LEGAL_HOLD_EMPTY_LIST
    result = runner.invoke(cli, ["legal-hold", "list", "-f", "csv"], obj=cli_state)
    assert "Matter ID,Name,Description,Creator,Creation Date" not in result.output


def test_show_with_format_option_returns_expected_format(
    runner, cli_state, check_matter_accessible_success, get_user_id_success
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "-f", "csv"], obj=cli_state
    )

    assert (
        "legalHoldUid,name,description,active,creationDate,creator,holdPolicyUid,creator_username"
        in result.output
    )
    assert "88888" in result.output
    assert "Test_Matter" in result.output
    assert "942564422882759874" in result.output
    assert "legal_admin@example.com" in result.output
    assert "66666" in result.output
    assert "legal_admin@example.com" in result.output
