import pytest
from pandas import DataFrame
from pandas import testing
from py42.exceptions import Py42BadRequestError
from py42.response import Py42Response
from requests import HTTPError
from requests import Response

from code42cli import PRODUCT_NAME
from code42cli.cmds.legal_hold import _build_user_dataframe
from code42cli.cmds.legal_hold import _check_matter_is_accessible
from code42cli.cmds.legal_hold import _get_total_archive_bytes_per_device
from code42cli.cmds.legal_hold import _merge_matter_members_with_devices
from code42cli.cmds.legal_hold import _print_storage_by_org
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
TEST_PRESERVATION_POLICY_UID = "1010101010"
ACTIVE_TEST_DEVICE_GUID = "853543498784654695"
INACTIVE_TEST_DEVICE_GUID = "987879465123464477"
MATTER_RESPONSE = """
{
    "legalHoldUid": "88888",
    "name": "Test_Matter",
    "description": "",
    "notes": null,
    "holdExtRef": null,
    "active": true,
    "creationDate": "2020-01-01T00:00:00.000-06:00",
    "lastModified": "2019-12-19T20:32:10.781Z",
    "creator": {
        "userUid": "12345",
        "username": "creator@example.com",
        "email": "user@example.com",
        "userExtRef": null
    },
    "holdPolicyUid": "66666"
}
"""
TEST_DEVICE_PAGE = {
    "computers": [
        {
            "computerId": 1111111,
            "name": "shouldprint",
            "osHostname": "UNKNOWN",
            "guid": "853543498784654695",
            "type": "COMPUTER",
            "status": "Active, Deauthorized",
            "active": "True",
            "blocked": "False",
            "alertState": 2,
            "alertStates": ["CriticalConnectionAlert"],
            "userId": "12345",
            "userUid": "12345",
            "orgId": 521084,
            "orgUid": "926779929022980902",
            "computerExtRef": None,
            "notes": None,
            "parentComputerId": None,
            "parentComputerGuid": None,
            "lastConnected": "2020-03-16T17:06:50.774Z",
            "osName": "linux",
            "osVersion": "4.15.0-45-generic",
            "osArch": "amd64",
            "address": "xxx.xxx.x.xx:4242",
            "remoteAddress": "xxx.xx.xxx.xxx",
            "javaVersion": "1.8.0_144",
            "modelInfo": None,
            "timeZone": "America/Los_Angeles",
            "version": 1525200006700,
            "productVersion": "7.0.0",
            "buildVersion": 586,
            "creationDate": "2020-03-16T16:20:00.871Z",
            "modificationDate": "2020-09-03T13:32:02.383Z",
            "loginDate": "2020-03-16T16:52:18.900Z",
            "service": "CrashPlan",
            "backupUsage": [
                {
                    "targetComputerParentId": "null",
                    "targetComputerParentGuid": "null",
                    "targetComputerGuid": "632540230984925185",
                    "targetComputerName": "PROe Cloud, US - West",
                    "targetComputerOsName": "null",
                    "targetComputerType": "SERVER",
                    "selectedFiles": 0,
                    "selectedBytes": 0,
                    "todoFiles": 0,
                    "todoBytes": 0,
                    "archiveBytes": 99056,
                    "billableBytes": 99056,
                    "sendRateAverage": 0,
                    "completionRateAverage": 0,
                    "lastBackup": "null",
                    "lastCompletedBackup": "null",
                    "lastConnected": "null",
                    "lastMaintenanceDate": "2020-12-08T14:38:56.565-06:00",
                    "lastCompactDate": "2020-12-08T14:38:56.549-06:00",
                    "modificationDate": "2020-12-23T10:02:53.738-06:00",
                    "creationDate": "2020-04-06T16:50:44.353-05:00",
                    "using": "true",
                    "alertState": 16,
                    "alertStates": ["CriticalBackupAlert"],
                    "percentComplete": 0.0,
                    "storePointId": 12537,
                    "storePointName": "erf-sea-3",
                    "serverId": 160025225,
                    "serverGuid": "946058956729596234",
                    "serverName": "erf-sea",
                    "serverHostName": "https://web-erf-sea.crashplan.com",
                    "isProvider": "false",
                    "archiveGuid": "948688240625098914",
                    "archiveFormat": "ARCHIVE_V1",
                    "activity": {
                        "connected": "false",
                        "backingUp": "false",
                        "restoring": "false",
                        "timeRemainingInMs": 0,
                        "remainingFiles": 0,
                        "remainingBytes": 0,
                    },
                },
                {
                    "targetComputerParentId": "null",
                    "targetComputerParentGuid": "null",
                    "targetComputerGuid": "43",
                    "targetComputerName": "PROe Cloud, US",
                    "targetComputerOsName": "null",
                    "targetComputerType": "SERVER",
                    "selectedFiles": 63775,
                    "selectedBytes": 2434109067,
                    "todoFiles": 0,
                    "todoBytes": 0,
                    "archiveBytes": 1199319510,
                    "billableBytes": 2434109067,
                    "sendRateAverage": 10528400,
                    "completionRateAverage": 265154800,
                    "lastBackup": "2019-12-16T17:01:31.749-06:00",
                    "lastCompletedBackup": "2019-12-16T17:01:31.749-06:00",
                    "lastConnected": "2019-12-16T17:04:12.818-06:00",
                    "lastMaintenanceDate": "2020-11-19T20:02:02.054-06:00",
                    "lastCompactDate": "2020-11-19T20:02:02.051-06:00",
                    "modificationDate": "2020-12-23T06:58:08.684-06:00",
                    "creationDate": "2019-11-25T16:16:38.692-06:00",
                    "using": "true",
                    "alertState": 16,
                    "alertStates": ["CriticalBackupAlert"],
                    "percentComplete": 100.0,
                    "storePointId": 9788,
                    "storePointName": "eda-iad-1",
                    "serverId": 160023585,
                    "serverGuid": "829383329462096515",
                    "serverName": "eda-iad",
                    "serverHostName": "https://web-eda-iad.crashplan.com",
                    "isProvider": "false",
                    "archiveGuid": "929857309487839252",
                    "archiveFormat": "ARCHIVE_V1",
                    "activity": {
                        "connected": "false",
                        "backingUp": "false",
                        "restoring": "false",
                        "timeRemainingInMs": 0,
                        "remainingFiles": 0,
                        "remainingBytes": 0,
                    },
                },
            ],
        },
        {
            "computerId": 2222222,
            "name": "shouldNotPrint",
            "osHostname": "UNKNOWN",
            "guid": "987879465123464477",
            "type": "COMPUTER",
            "status": "Active",
            "active": "True",
            "blocked": "False",
            "alertState": 0,
            "alertStates": ["OK"],
            "userId": "02345",
            "userUid": "02345",
            "orgId": 521084,
            "orgUid": "926779929022980902",
            "computerExtRef": None,
            "notes": None,
            "parentComputerId": None,
            "parentComputerGuid": None,
            "lastConnected": "2018-03-19T20:04:02.999Z",
            "osName": "win",
            "osVersion": "10.0.18362",
            "osArch": "amd64",
            "address": "xxx.x.xx.xxx:4242",
            "remoteAddress": "xx.xx.xxx.xxx",
            "javaVersion": "11.04",
            "modelInfo": None,
            "timeZone": "America/Chicago",
            "version": 1525200006770,
            "productVersion": "7.7.0",
            "buildVersion": 833,
            "creationDate": "2020-03-19T19:43:16.918Z",
            "modificationDate": "2020-09-08T15:43:45.875Z",
            "loginDate": "2020-03-19T20:03:45.360Z",
            "service": "CrashPlan",
            "backupUsage": [
                {
                    "targetComputerParentId": "null",
                    "targetComputerParentGuid": "null",
                    "targetComputerGuid": "632540230984925185",
                    "targetComputerName": "PROe Cloud, US - West",
                    "targetComputerOsName": "null",
                    "targetComputerType": "SERVER",
                    "selectedFiles": 0,
                    "selectedBytes": 0,
                    "todoFiles": 0,
                    "todoBytes": 0,
                    "archiveBytes": 99056,
                    "billableBytes": 99056,
                    "sendRateAverage": 0,
                    "completionRateAverage": 0,
                    "lastBackup": "null",
                    "lastCompletedBackup": "null",
                    "lastConnected": "null",
                    "lastMaintenanceDate": "2020-12-08T14:38:56.565-06:00",
                    "lastCompactDate": "2020-12-08T14:38:56.549-06:00",
                    "modificationDate": "2020-12-23T10:02:53.738-06:00",
                    "creationDate": "2020-04-06T16:50:44.353-05:00",
                    "using": "true",
                    "alertState": 16,
                    "alertStates": ["CriticalBackupAlert"],
                    "percentComplete": 0.0,
                    "storePointId": 12537,
                    "storePointName": "erf-sea-3",
                    "serverId": 160025225,
                    "serverGuid": "946058956729596234",
                    "serverName": "erf-sea",
                    "serverHostName": "https://web-erf-sea.crashplan.com",
                    "isProvider": "false",
                    "archiveGuid": "948688240625098914",
                    "archiveFormat": "ARCHIVE_V1",
                    "activity": {
                        "connected": "false",
                        "backingUp": "false",
                        "restoring": "false",
                        "timeRemainingInMs": 0,
                        "remainingFiles": 0,
                        "remainingBytes": 0,
                    },
                },
                {
                    "targetComputerParentId": "null",
                    "targetComputerParentGuid": "null",
                    "targetComputerGuid": "43",
                    "targetComputerName": "PROe Cloud, US",
                    "targetComputerOsName": "null",
                    "targetComputerType": "SERVER",
                    "selectedFiles": 63775,
                    "selectedBytes": 2434109067,
                    "todoFiles": 0,
                    "todoBytes": 0,
                    "archiveBytes": 1199319510,
                    "billableBytes": 2434109067,
                    "sendRateAverage": 10528400,
                    "completionRateAverage": 265154800,
                    "lastBackup": "2019-12-16T17:01:31.749-06:00",
                    "lastCompletedBackup": "2019-12-16T17:01:31.749-06:00",
                    "lastConnected": "2019-12-16T17:04:12.818-06:00",
                    "lastMaintenanceDate": "2020-11-19T20:02:02.054-06:00",
                    "lastCompactDate": "2020-11-19T20:02:02.051-06:00",
                    "modificationDate": "2020-12-23T06:58:08.684-06:00",
                    "creationDate": "2019-11-25T16:16:38.692-06:00",
                    "using": "true",
                    "alertState": 16,
                    "alertStates": ["CriticalBackupAlert"],
                    "percentComplete": 100.0,
                    "storePointId": 9788,
                    "storePointName": "eda-iad-1",
                    "serverId": 160023585,
                    "serverGuid": "829383329462096515",
                    "serverName": "eda-iad",
                    "serverHostName": "https://web-eda-iad.crashplan.com",
                    "isProvider": "false",
                    "archiveGuid": "929857309487839252",
                    "archiveFormat": "ARCHIVE_V1",
                    "activity": {
                        "connected": "false",
                        "backingUp": "false",
                        "restoring": "false",
                        "timeRemainingInMs": 0,
                        "remainingFiles": 0,
                        "remainingBytes": 0,
                    },
                },
            ],
        },
    ]
}
USERS_LIST = [
    [True, "12345", "user@example.com"],
    [False, "02345", "inactive@example.com"],
]
POLICY_RESPONSE = """
{
    "legalHoldPolicyUid": "1010101010",
    "name": "Test",
    "creatorUser": {
        "userUid": "12345",
        "userId": 12345,
        "username": "user@example.com",
        "email": "user@example.com",
        "firstName": "User",
        "lastName": "User"
    },
    "policy": {
        "backupOpenFiles": true,
        "compression": "ON",
        "dataDeDupAutoMaxFileSizeForLan": 1000000000,
        "dataDeDupAutoMaxFileSizeForWan": 1000000000,
        "dataDeDuplication": "FULL",
        "encryptionEnabled": true,
        "scanIntervalMillis": 86400000,
        "scanTime": "03:00",
        "watchFiles": true,
        "destinations": [],
        "backupRunWindow": {
            "alwaysRun": true,
            "startTimeOfDay": "01:00",
            "endTimeOfDay": "06:00",
            "days": ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        },
        "backupPaths": {
            "paths": [],
            "excludePatterns": {
                "windows": [],
                "linux": [],
                "macintosh": [],
                "all": []
            }
        },
        "retentionPolicy": {
            "backupFrequencyMillis": 900000,
            "keepDeleted": true,
            "keepDeletedMinutes": 0,
            "versionLastWeekIntervalMinutes": 15,
            "versionLastNinetyDaysIntervalMinutes": 1440,
            "versionLastYearIntervalMinutes": 10080,
            "versionPrevYearsIntervalMinutes": 43200
        }
    },
    "creationDate": "2019-05-14T16:19:09.930Z",
    "modificationDate": "2019-05-14T16:19:09.930Z"
}
"""
EMPTY_CUSTODIANS_RESPONSE = """{"legalHoldMemberships": []}"""
ALL_ACTIVE_CUSTODIANS_RESPONSE = """
{
    "legalHoldMemberships": [
        {
            "legalHoldMembershipUid": "88888",
            "active": true,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "12345",
                "username": "user@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        }
    ]
}
"""
ALL_INACTIVE_CUSTODIANS_RESPONSE = """
{
    "legalHoldMemberships": [
        {
            "legalHoldMembershipUid": "88888",
            "active": false,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "02345",
                "username": "inactive@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        }
    ]
}
"""
ALL_ACTIVE_AND_INACTIVE_CUSTODIANS_RESPONSE = """
{
    "legalHoldMemberships": [
        {
            "legalHoldMembershipUid": "88888",
            "active": true,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "12345",
                "username": "user@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        },
        {
            "legalHoldMembershipUid": "88888",
            "active": false,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "02345",
                "username": "inactive@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        }
    ]
}
"""
EMPTY_MATTERS_RESPONSE = """{"legalHolds": []}"""
ALL_MATTERS_RESPONSE = """{{"legalHolds": [{}]}}""".format(MATTER_RESPONSE)


def _create_py42_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return Py42Response(response)


@pytest.fixture
def matter_response(mocker):
    return _create_py42_response(mocker, MATTER_RESPONSE)


@pytest.fixture
def preservation_policy_response(mocker):
    return _create_py42_response(mocker, POLICY_RESPONSE)


@pytest.fixture
def devices_list_generator(mocker):
    return [TEST_DEVICE_PAGE]


@pytest.fixture
def empty_legal_hold_memberships_response(mocker):
    return [_create_py42_response(mocker, EMPTY_CUSTODIANS_RESPONSE)]


@pytest.fixture
def active_legal_hold_memberships_response(mocker):
    return [_create_py42_response(mocker, ALL_ACTIVE_CUSTODIANS_RESPONSE)]


@pytest.fixture
def inactive_legal_hold_memberships_response(mocker):
    return [_create_py42_response(mocker, ALL_INACTIVE_CUSTODIANS_RESPONSE)]


@pytest.fixture
def active_and_inactive_legal_hold_memberships_response(mocker):
    return [_create_py42_response(mocker, ALL_ACTIVE_AND_INACTIVE_CUSTODIANS_RESPONSE)]


@pytest.fixture
def get_user_id_success(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {
        "users": [{"userUid": ACTIVE_TEST_USER_ID}]
    }


@pytest.fixture
def empty_matters_response(mocker):
    return [_create_py42_response(mocker, EMPTY_MATTERS_RESPONSE)]


@pytest.fixture
def all_matters_response(mocker):
    return [_create_py42_response(mocker, ALL_MATTERS_RESPONSE)]


@pytest.fixture
def get_user_id_failure(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {"users": []}


@pytest.fixture
def check_matter_accessible_success(cli_state, matter_response):
    cli_state.sdk.legalhold.get_matter_by_uid.return_value = matter_response


@pytest.fixture
def get_all_devices_success(cli_state, devices_list_generator):
    cli_state.sdk.devices.get_all.return_value = devices_list_generator


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
    runner,
    cli_state,
    check_matter_accessible_success,
    get_user_id_success,
    empty_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        empty_legal_hold_memberships_response
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
    runner,
    cli_state,
    check_matter_accessible_success,
    get_user_id_success,
    active_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_legal_hold_memberships_response
    )
    membership_uid = "88888"
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
    runner,
    cli_state,
    check_matter_accessible_success,
    active_and_inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_and_inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME in result.output


def test_show_matter_prints_active_results_only(
    runner,
    cli_state,
    check_matter_accessible_success,
    active_and_inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_and_inactive_legal_hold_memberships_response
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME not in result.output


def test_show_matter_prints_no_active_members_when_no_membership(
    runner,
    cli_state,
    check_matter_accessible_success,
    empty_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        empty_legal_hold_memberships_response
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME not in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_no_inactive_members_when_no_inactive_membership(
    runner,
    cli_state,
    check_matter_accessible_success,
    active_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME not in result.output
    assert "No inactive matter members." in result.output


def test_show_matter_prints_no_active_members_when_no_active_membership(
    runner,
    cli_state,
    check_matter_accessible_success,
    inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_no_active_members_when_no_active_membership_and_inactive_membership_included(
    runner,
    cli_state,
    check_matter_accessible_success,
    inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_devices_when_active_user_has_devices_if_device_flag_is_set(
    runner,
    cli_state,
    active_legal_hold_memberships_response,
    check_matter_accessible_success,
    get_all_devices_success,
):

    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-devices"], obj=cli_state
    )

    assert ACTIVE_TEST_DEVICE_GUID in result.output
    assert INACTIVE_TEST_DEVICE_GUID not in result.output


def test_show_matter_prints_devices_when_inactive_user_has_devices_if_device_and_inactive_flag_is_set(
    runner,
    cli_state,
    active_and_inactive_legal_hold_memberships_response,
    check_matter_accessible_success,
    get_all_devices_success,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_and_inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "show",
            TEST_MATTER_ID,
            "--include-devices",
            "--include-inactive",
        ],
        obj=cli_state,
    )

    assert ACTIVE_TEST_DEVICE_GUID in result.output
    assert INACTIVE_TEST_DEVICE_GUID in result.output


def test_show_matter_prints_no_device_table_if_no_devices_found_when_include_devices_flag_set(
    runner,
    cli_state,
    active_and_inactive_legal_hold_memberships_response,
    check_matter_accessible_success,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_and_inactive_legal_hold_memberships_response
    )
    cli_state.sdk.devices.get_all.return_value = {}
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "show",
            TEST_MATTER_ID,
            "--include-devices",
            "--include-inactive",
        ],
        obj=cli_state,
    )

    assert "No devices associated with matter." in result.output
    assert "Matter Members and Devices:" not in result.output
    assert "Legal Hold Storage by Org" not in result.output
    assert "osHostname" not in result.output
    assert "alertStates" not in result.output


def test_show_matter_device_dataframe_returns_correct_columns(cli_state):
    user_dataframe = _build_user_dataframe(USERS_LIST)
    result = _merge_matter_members_with_devices(cli_state.sdk, user_dataframe)
    assert "userUid" in result.columns
    assert "username" in result.columns
    assert "activeMembership" in result.columns
    assert "guid" in result.columns
    assert "lastConnected" in result.columns
    assert "archiveBytes" in result.columns
    assert "backupUsage" not in result.columns


def test_show_matter_user_dataframe_returns_correct_columns_and_values():
    result = _build_user_dataframe(USERS_LIST)
    assert "userUid" in result.columns
    assert "username" in result.columns
    assert "activeMembership" in result.columns
    assert "guid" not in result.columns
    assert "12345" in result.values
    assert "user@example.com" in result.values


def test_show_matter_org_storage_dataframe_returns_correct_group_values():
    test_devices_dataframe = DataFrame(
        data={
            "orgId": [521084, 521084],
            "guid": ["853543498784654695", "926779929022980902"],
            "version": [1525200006770, 1525200006770],
            "archiveBytes": [1199418566, 1199418566],
        }
    )
    expected_return = DataFrame.from_records(
        [{"orgId": 521084, "archiveBytes": 2398837132}], index="orgId"
    )
    test_return = _print_storage_by_org(test_devices_dataframe)
    testing.assert_frame_equal(expected_return, test_return)


def test_show_matter_device_total_archive_bytes_are_calculated(devices_list_generator):
    result = _get_total_archive_bytes_per_device(devices_list_generator)
    assert "archiveBytes" in result[0].keys()
    assert result[0]["archiveBytes"] == (
        result[0]["backupUsage"][0]["archiveBytes"]
        + result[0]["backupUsage"][1]["archiveBytes"]
    )


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


def test_list_with_format_csv_returns_csv_format(
    runner, cli_state, all_matters_response
):
    cli_state.sdk.legalhold.get_all_matters.return_value = all_matters_response
    result = runner.invoke(cli, ["legal-hold", "list", "-f", "csv"], obj=cli_state)
    assert "legalHoldUid" in result.output
    assert "name" in result.output
    assert "description" in result.output
    assert "active" in result.output
    assert "creationDate" in result.output
    assert "lastModified" in result.output
    assert "creator" in result.output
    assert "holdPolicyUid" in result.output
    assert "creator_username" in result.output
    assert "88888" in result.output
    assert "Test_Matter" in result.output
    comma_count = [c for c in result.output if c == ","]
    assert len(comma_count) >= 13


def test_list_with_csv_format_returns_no_response_when_response_is_empty(
    runner, cli_state, empty_legal_hold_memberships_response, empty_matters_response
):
    cli_state.sdk.legalhold.get_all_matters.return_value = empty_matters_response
    result = runner.invoke(cli, ["legal-hold", "list", "-f", "csv"], obj=cli_state)
    assert "Matter ID,Name,Description,Creator,Creation Date" not in result.output
