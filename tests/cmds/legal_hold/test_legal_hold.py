import pytest

from requests import Response, HTTPError

from code42cli import PRODUCT_NAME
from code42cli.cmds.legal_hold import (
    add_user,
    remove_user,
    show_matter,
    add_bulk_users,
    remove_bulk_users,
    _check_matter_is_accessible,
)
from code42cli.errors import (
    UserAlreadyAddedError,
    UserNotInLegalHoldError,
    LegalHoldNotFoundOrPermissionDeniedError,
    UserDoesNotExistError,
)

_NAMESPACE = "{}.cmds.legal_hold".format(PRODUCT_NAME)

from py42.exceptions import Py42BadRequestError
from py42.response import Py42Response
from requests import Response

from ...conftest import create_mock_reader

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
ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT = [{"legalHoldMemberships": [ACTIVE_LEGAL_HOLD_MEMBERSHIP]}]
ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT = [
    {"legalHoldMemberships": [ACTIVE_LEGAL_HOLD_MEMBERSHIP, INACTIVE_LEGAL_HOLD_MEMBERSHIP]}
]
INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT = [
    {"legalHoldMemberships": [INACTIVE_LEGAL_HOLD_MEMBERSHIP]}
]

TEST_PRESERVATION_POLICY_UID = "1010101010"
TEST_PRESERVATION_POLICY_JSON = '{{"creationDate": "2020-01-01","legalHoldPolicyUid": {}}}'.format(
    TEST_PRESERVATION_POLICY_UID
)


@pytest.fixture
def preservation_policy_response(mocker):
    response = mocker.MagicMock(spec=Response)
    response.text = TEST_PRESERVATION_POLICY_JSON
    return Py42Response(response)


@pytest.fixture
def get_user_id_success(sdk):
    sdk.users.get_by_username.return_value = {"users": [{"userUid": ACTIVE_TEST_USER_ID}]}


@pytest.fixture
def get_user_id_failure(sdk):
    sdk.users.get_by_username.return_value = {"users": []}


@pytest.fixture
def check_matter_accessible_success(sdk):
    sdk.legalhold.get_matter_by_uid.return_value = TEST_MATTER_RESULT


@pytest.fixture
def check_matter_accessible_failure(sdk):
    sdk.legalhold.get_matter_by_uid.side_effect = Py42BadRequestError(HTTPError())


@pytest.fixture
def user_already_added_response(mocker):
    mock_response = mocker.MagicMock(spec=Response)
    mock_response.text = "USER_ALREADY_IN_HOLD"
    http_error = HTTPError()
    http_error.response = mock_response
    return Py42BadRequestError(http_error)


def test_add_user_raises_user_already_added_error_when_user_already_on_hold(
    sdk, user_already_added_response
):
    sdk.legalhold.add_to_matter.side_effect = user_already_added_response
    with pytest.raises(UserAlreadyAddedError):
        add_user(sdk, TEST_MATTER_ID, ACTIVE_TEST_USERNAME)


def test_add_user_raises_legalhold_not_found_error_if_matter_inaccessible(
    sdk, check_matter_accessible_failure, get_user_id_success
):
    with pytest.raises(LegalHoldNotFoundOrPermissionDeniedError):
        add_user(sdk, TEST_MATTER_ID, ACTIVE_TEST_USERNAME)


def test_add_user_adds_user_to_hold_if_user_and_matter_exist(
    sdk, check_matter_accessible_success, get_user_id_success
):
    add_user(sdk, TEST_MATTER_ID, ACTIVE_TEST_USERNAME)
    sdk.legalhold.add_to_matter.assert_called_once_with(ACTIVE_TEST_USER_ID, TEST_MATTER_ID)


def test_remove_user_raises_legalhold_not_found_error_if_matter_inaccessible(
    sdk, check_matter_accessible_failure, get_user_id_success
):
    with pytest.raises(LegalHoldNotFoundOrPermissionDeniedError):
        remove_user(sdk, TEST_MATTER_ID, ACTIVE_TEST_USERNAME)


def test_remove_user_raises_user_not_in_matter_error_if_user_not_active_in_matter(
    sdk, check_matter_accessible_success, get_user_id_success
):
    sdk.legalhold.get_all_matter_custodians.return_value = EMPTY_LEGAL_HOLD_MEMBERSHIPS_RESULT
    with pytest.raises(UserNotInLegalHoldError):
        remove_user(sdk, TEST_MATTER_ID, ACTIVE_TEST_USERNAME)


def test_remove_user_removes_user_if_user_in_matter(
    sdk, check_matter_accessible_success, get_user_id_success
):
    sdk.legalhold.get_all_matter_custodians.return_value = ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    membership_uid = ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT[0]["legalHoldMemberships"][0][
        "legalHoldMembershipUid"
    ]
    remove_user(sdk, TEST_MATTER_ID, ACTIVE_TEST_USERNAME)
    sdk.legalhold.remove_from_matter.assert_called_with(membership_uid)


def test_matter_accessible_check_only_makes_one_http_call_when_called_multiple_times_with_same_matter_id(
    sdk, check_matter_accessible_success
):
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    assert sdk.legalhold.get_matter_by_uid.call_count == 1


def test_show_matter_prints_active_and_inactive_results_when_include_inactive_flag_set(
    sdk, check_matter_accessible_success, capsys
):
    sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    show_matter(sdk, TEST_MATTER_ID, include_inactive=True)
    capture = capsys.readouterr()
    assert ACTIVE_TEST_USERNAME in capture.out
    assert INACTIVE_TEST_USERNAME in capture.out


def test_show_matter_prints_active_results_only(sdk, check_matter_accessible_success, capsys):
    sdk.legalhold.get_all_matter_custodians.return_value = (
        ACTIVE_AND_INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    )
    show_matter(sdk, TEST_MATTER_ID)
    capture = capsys.readouterr()
    assert ACTIVE_TEST_USERNAME in capture.out
    assert INACTIVE_TEST_USERNAME not in capture.out


def test_show_matter_prints_no_active_members_when_no_membership(
    sdk, check_matter_accessible_success, capsys
):
    sdk.legalhold.get_all_matter_custodians.return_value = EMPTY_LEGAL_HOLD_MEMBERSHIPS_RESULT
    show_matter(sdk, TEST_MATTER_ID)
    capture = capsys.readouterr()
    assert ACTIVE_TEST_USERNAME not in capture.out
    assert INACTIVE_TEST_USERNAME not in capture.out
    assert "No active matter members." in capture.out


def test_show_matter_prints_no_inactive_members_when_no_inactive_membership(
    sdk, check_matter_accessible_success, capsys
):
    sdk.legalhold.get_all_matter_custodians.return_value = ACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    show_matter(sdk, TEST_MATTER_ID, include_inactive=True)
    capture = capsys.readouterr()
    assert ACTIVE_TEST_USERNAME in capture.out
    assert INACTIVE_TEST_USERNAME not in capture.out
    assert "No inactive matter members." in capture.out


def test_show_matter_prints_no_active_members_when_no_active_membership(
    sdk, check_matter_accessible_success, capsys
):
    sdk.legalhold.get_all_matter_custodians.return_value = INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    show_matter(sdk, TEST_MATTER_ID, include_inactive=True)
    capture = capsys.readouterr()
    assert ACTIVE_TEST_USERNAME not in capture.out
    assert INACTIVE_TEST_USERNAME in capture.out
    assert "No active matter members." in capture.out


def test_show_matter_prints_no_active_members_when_no_active_membership_and_inactive_membership_included(
    sdk, check_matter_accessible_success, capsys
):
    sdk.legalhold.get_all_matter_custodians.return_value = INACTIVE_LEGAL_HOLD_MEMBERSHIPS_RESULT
    show_matter(sdk, TEST_MATTER_ID, include_inactive=True)
    capture = capsys.readouterr()
    assert ACTIVE_TEST_USERNAME not in capture.out
    assert INACTIVE_TEST_USERNAME in capture.out
    assert "No active matter members." in capture.out


def test_show_matter_prints_preservation_policy_when_include_policy_flag_set(
    sdk, check_matter_accessible_success, preservation_policy_response, capsys
):
    sdk.legalhold.get_policy_by_uid.return_value = preservation_policy_response
    show_matter(sdk, TEST_MATTER_ID, include_policy=True)
    capture = capsys.readouterr()
    assert TEST_PRESERVATION_POLICY_UID in capture.out


def test_show_matter_does_not_print_preservation_policy(
    sdk, check_matter_accessible_success, preservation_policy_response, capsys
):
    sdk.legalhold.get_policy_by_uid.return_value = preservation_policy_response
    show_matter(sdk, TEST_MATTER_ID)
    capture = capsys.readouterr()
    assert TEST_PRESERVATION_POLICY_UID not in capture.out


def test_add_bulk_users_uses_expected_arguments(mocker, sdk, profile):
    reader = create_mock_reader([{"test": "value"}])
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    reader_factory = mocker.patch("{}.create_csv_reader".format(_NAMESPACE))
    reader_factory.return_value = reader
    add_bulk_users(sdk, "csv_test")
    assert bulk_processor.call_args[0][1] == reader
    reader_factory.assert_called_once_with("csv_test")


def test_remove_bulk_users_uses_expected_arguments(mocker, sdk, profile):
    reader = create_mock_reader([{"test": "value"}])
    bulk_processor = mocker.patch("{}.run_bulk_process".format(_NAMESPACE))
    reader_factory = mocker.patch("{}.create_csv_reader".format(_NAMESPACE))
    reader_factory.return_value = reader
    remove_bulk_users(sdk, "csv_test")
    assert bulk_processor.call_args[0][1] == reader
    reader_factory.assert_called_once_with("csv_test")
