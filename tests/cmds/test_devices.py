import json
from datetime import date

import numpy as np
import pytest
from pandas import DataFrame
from pandas import Series
from pandas._testing import assert_frame_equal
from pandas._testing import assert_series_equal
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42NotFoundError
from py42.exceptions import Py42OrgNotFoundError
from tests.conftest import create_mock_response

from code42cli.cmds.devices import _add_backup_set_settings_to_dataframe
from code42cli.cmds.devices import _add_legal_hold_membership_to_device_dataframe
from code42cli.cmds.devices import _add_usernames_to_device_dataframe
from code42cli.cmds.devices import _break_backup_usage_into_total_storage
from code42cli.cmds.devices import _get_device_dataframe
from code42cli.main import cli
from code42cli.worker import WorkerStats

_NAMESPACE = "code42cli.cmds.devices"
TEST_NEW_DEVICE_NAME = "test-new-device-name-123"
TEST_DATE_OLDER = "2020-01-01T12:00:00.774Z"
TEST_DATE_NEWER = "2021-01-01T12:00:00.774Z"
TEST_DATE_MIDDLE = "2020-06-01T12:00:00"
TEST_DEVICE_GUID = "954143368874689941"
TEST_DEVICE_ID = 139527
TEST_ARCHIVE_GUID = "954143426849296547"
TEST_PURGE_DATE = "2020-10-12"
TEST_ARCHIVES_RESPONSE = {
    "archives": [
        {
            "archiveGuid": "954143426849296547",
            "userId": None,
            "userUid": None,
            "archiveBytes": 1745757673,
            "targetGuid": "632540230984925185",
            "lastCompletedBackup": "2020-10-12T20:17:52.084Z",
            "isColdStorage": False,
            "lastMaintained": "2020-10-10T19:31:05.811Z",
            "maintenanceDuration": 455,
            "compactBytesRemoved": 0,
            "storePointId": 1000,
            "selectedBytes": 1658317953,
            "selectedFiles": 596,
            "todoBytes": 0,
            "format": "ARCHIVE_V1",
        }
    ]
}
TEST_DEVICE_RESPONSE = """{"data":{"computerId":139527,"name":"testname","osHostname":
"testhostname","guid":"954143368874689941","type":"COMPUTER","status":"Active","active":true,
"blocked":false,"alertState":0,"alertStates":["OK"],"userId":203988,"userUid":"938960273869958201",
"orgId":3099,"orgUid":"915323705751579872","computerExtRef":null,"notes":null,"parentComputerId":
null,"parentComputerGuid":null,"lastConnected":"2020-10-12T16:55:40.632Z","osName":"win",
"osVersion":"10.0.18362","osArch":"amd64","address":"172.16.208.140:4242","remoteAddress":
"72.50.201.186","javaVersion":"11.0.4","modelInfo":null,"timeZone":"America/Chicago",
"version":1525200006822,"productVersion":"8.2.2","buildVersion":26,"creationDate":
"2020-05-14T13:03:20.302Z","modificationDate":"2020-10-12T16:55:40.632Z","loginDate":
"2020-10-12T12:54:45.132Z","service":"CrashPlan"}}"""
TEST_BACKUPUSAGE_RESPONSE = """{"metadata":{"timestamp":"2020-10-13T12:51:28.410Z",
"params":{"incBackupUsage":"True","idType":"guid"}},"data":{"computerId":1767,"name":
"SNWINTEST1","osHostname":"UNKNOWN","guid":"843290890230648046","type":"COMPUTER",
"status":"Active","active":true,"blocked":false,"alertState":2,"alertStates":
["CriticalConnectionAlert"],"userId":1934,"userUid":"843290130258496632","orgId":1067,
"orgUid":"843284512172838008","computerExtRef":null,"notes":null,"parentComputerId":null,
"parentComputerGuid":null,"lastConnected":"2018-04-13T20:57:12.496Z","osName":"win",
"osVersion":"10.0","osArch":"amd64","address":"10.0.1.23:4242","remoteAddress":"73.53.78.104",
"javaVersion":"1.8.0_144","modelInfo":null,"timeZone":"America/Los_Angeles","version":
1512021600671,"productVersion":"6.7.1","buildVersion":4615,"creationDate":"2018-04-10T19:23:23.564Z",
"modificationDate":"2018-06-29T17:41:12.616Z","loginDate":"2018-04-13T20:17:32.213Z","service":
"CrashPlan","backupUsage":[{"targetComputerParentId":null,"targetComputerParentGuid":null,
"targetComputerGuid":"632540230984925185","targetComputerName":"Code42 Cloud USA West",
"targetComputerOsName":null,"targetComputerType":"SERVER","selectedFiles":0,"selectedBytes":0,
"todoFiles":0,"todoBytes":0,"archiveBytes":119501,"billableBytes":119501,"sendRateAverage":0,
"completionRateAverage":0,"lastBackup":null,"lastCompletedBackup":null,"lastConnected":
"2018-04-11T16:23:35.776Z","lastMaintenanceDate":"2020-10-08T21:23:12.533Z","lastCompactDate":
"2020-10-08T21:23:12.411Z","modificationDate":"2020-10-12T16:19:01.267Z","creationDate":
"2018-04-10T19:48:29.903Z","using":true,"alertState":16,"alertStates":["CriticalBackupAlert"],
"percentComplete":0.0,"storePointId":1001,"storePointName":"cif-sea-2","serverId":1003,"serverGuid":
"836476656572622471","serverName":"cif-sea","serverHostName":"https://cif-sea.crashplan.com",
"isProvider":false,"archiveGuid":"843293524842941560","archiveFormat":"ARCHIVE_V1","activity":
{"connected":false,"backingUp":false,"restoring":false,"timeRemainingInMs":0,
"remainingFiles":0,"remainingBytes":0}},{"targetComputerParentId":null,"targetComputerParentGuid":
null,"targetComputerGuid":"43","targetComputerName":"PROe Cloud, US","targetComputerOsName":null,
"targetComputerType":"SERVER","selectedFiles":1599,"selectedBytes":1529420143,"todoFiles":0,
"todoBytes":0,"archiveBytes":56848550,"billableBytes":1529420143,"sendRateAverage":0,
"completionRateAverage":0,"lastBackup":"2019-12-02T09:34:28.364-06:00","lastCompletedBackup":
"2019-12-02T09:34:28.364-06:00","lastConnected":"2019-12-02T11:02:36.108-06:00","lastMaintenanceDate":
"2021-02-16T07:01:11.697-06:00","lastCompactDate":"2021-02-16T07:01:11.694-06:00","modificationDate":
"2021-02-17T04:57:27.222-06:00","creationDate":"2019-09-26T15:27:38.806-05:00","using":true,
"alertState":16,"alertStates":["CriticalBackupAlert"],"percentComplete":100.0,"storePointId":10989,
"storePointName":"fsa-iad-2","serverId":160024121,"serverGuid":"883282371081742804","serverName":
"fsa-iad","serverHostName":"https://web-fsa-iad.crashplan.com","isProvider":false,"archiveGuid":
"92077743916530001","archiveFormat":"ARCHIVE_V1","activity":{"connected":false,"backingUp":false,
"restoring":false,"timeRemainingInMs":0,"remainingFiles":0,"remainingBytes":0}}]}}"""
TEST_EMPTY_BACKUPUSAGE_RESPONSE = """{"metadata":{"timestamp":"2020-10-13T12:51:28.410Z","params":
{"incBackupUsage":"True","idType":"guid"}},"data":{"computerId":1767,"name":"SNWINTEST1",
"osHostname":"UNKNOWN","guid":"843290890230648046","type":"COMPUTER","status":"Active",
"active":true,"blocked":false,"alertState":2,"alertStates":["CriticalConnectionAlert"],
"userId":1934,"userUid":"843290130258496632","orgId":1067,"orgUid":"843284512172838008",
"computerExtRef":null,"notes":null,"parentComputerId":null,"parentComputerGuid":null,"lastConnected":
"2018-04-13T20:57:12.496Z","osName":"win","osVersion":"10.0","osArch":"amd64","address":
"10.0.1.23:4242","remoteAddress":"73.53.78.104","javaVersion":"1.8.0_144","modelInfo":null,
"timeZone":"America/Los_Angeles","version":1512021600671,"productVersion":"6.7.1","buildVersion":
4615,"creationDate":"2018-04-10T19:23:23.564Z","modificationDate":"2018-06-29T17:41:12.616Z",
"loginDate":"2018-04-13T20:17:32.213Z","service":"CrashPlan","backupUsage":[]}}"""
TEST_COMPUTER_PAGE = {
    "computers": [
        {
            "computerId": 1207,
            "name": "ubuntu",
            "osHostname": "UNKNOWN",
            "guid": "839648314463407622",
            "type": "COMPUTER",
            "status": "Active, Deauthorized",
            "active": True,
            "blocked": False,
            "alertState": 2,
            "alertStates": ["CriticalConnectionAlert"],
            "userId": 1320,
            "userUid": "840103986007089121",
            "orgId": 1017,
            "orgUid": "836473214639515393",
            "computerExtRef": None,
            "notes": None,
            "parentComputerId": None,
            "parentComputerGuid": None,
            "lastConnected": TEST_DATE_OLDER,
            "osName": "linux",
            "osVersion": "4.4.0-96-generic",
            "osArch": "amd64",
            "address": "172.16.132.193:4242",
            "remoteAddress": "38.92.134.129",
            "javaVersion": "1.8.0_144",
            "modelInfo": None,
            "timeZone": "America/Chicago",
            "version": 1512021600671,
            "productVersion": "6.7.1",
            "buildVersion": 4589,
            "creationDate": TEST_DATE_OLDER,
            "modificationDate": "2020-09-03T13:32:02.383Z",
            "loginDate": "2018-03-16T16:52:18.900Z",
            "service": "CrashPlan",
        },
        {
            "computerId": 1281,
            "name": "TOM-PC",
            "osHostname": "UNKNOWN",
            "guid": "840099921260026634",
            "type": "COMPUTER",
            "status": "Deactivated",
            "active": False,
            "blocked": False,
            "alertState": 0,
            "alertStates": ["OK"],
            "userId": 1320,
            "userUid": "840103986007089121",
            "orgId": 1034,
            "orgUid": "840098081282695137",
            "computerExtRef": None,
            "notes": None,
            "parentComputerId": None,
            "parentComputerGuid": None,
            "lastConnected": TEST_DATE_NEWER,
            "osName": "win",
            "osVersion": "6.1",
            "osArch": "amd64",
            "address": "172.16.3.34:4242",
            "remoteAddress": "38.92.134.129",
            "javaVersion": "1.8.0_121",
            "modelInfo": None,
            "timeZone": "America/Chicago",
            "version": 1508734800652,
            "productVersion": "6.5.2",
            "buildVersion": 32,
            "creationDate": TEST_DATE_NEWER,
            "modificationDate": "2020-09-08T15:43:45.875Z",
            "loginDate": "2018-03-19T20:03:45.360Z",
            "service": "CrashPlan",
        },
    ]
}
TEST_USERS_LIST_PAGE = {
    "totalCount": 2,
    "users": [
        {
            "userId": 1320,
            "userUid": "840103986007089121",
            "status": "Active",
            "username": "ttranda_deactivated@ttrantest.com",
            "email": "ttranda@ttrantest.com",
            "firstName": "Thomas",
            "lastName": "Tran",
            "quotaInBytes": -1,
            "orgId": 1034,
            "orgUid": "840098081282695137",
            "orgName": "Okta SSO",
            "userExtRef": None,
            "notes": None,
            "active": True,
            "blocked": False,
            "emailPromo": True,
            "invited": False,
            "orgType": "ENTERPRISE",
            "usernameIsAnEmail": True,
            "creationDate": "2018-03-19T19:43:16.742Z",
            "modificationDate": "2018-10-26T20:22:05.726Z",
            "passwordReset": False,
            "localAuthenticationOnly": False,
            "licenses": ["admin.securityTools"],
        },
        {
            "userId": 1014,
            "userUid": "836473273124890369",
            "status": "Active",
            "username": "test@example.com",
            "email": "test@example.com",
            "firstName": "Chad",
            "lastName": "Valentine",
            "quotaInBytes": -1,
            "orgId": 1017,
            "orgUid": "836473214639515393",
            "orgName": "Holy SaaS-a-roli",
            "userExtRef": None,
            "notes": None,
            "active": True,
            "blocked": False,
            "emailPromo": True,
            "invited": False,
            "orgType": "ENTERPRISE",
            "usernameIsAnEmail": True,
            "creationDate": "2018-02-22T18:35:23.217Z",
            "modificationDate": "2018-04-25T11:12:11.504Z",
            "passwordReset": False,
            "localAuthenticationOnly": False,
            "licenses": ["admin.securityTools"],
        },
    ],
}
MATTER_RESPONSE = {
    "legalHolds": [
        {
            "legalHoldUid": "123456789",
            "name": "Test legal hold matter",
            "description": "",
            "notes": None,
            "holdExtRef": None,
            "active": True,
            "creationDate": "2020-08-05T10:49:58.353-05:00",
            "lastModified": "2020-08-05T10:49:58.358-05:00",
            "creator": {
                "userUid": "12345",
                "username": "user@code42.com",
                "email": "user@code42.com",
                "userExtRef": None,
            },
            "holdPolicyUid": "966191295667423997",
        },
        {
            "legalHoldUid": "987654321",
            "name": "Another Matter",
            "description": "",
            "notes": None,
            "holdExtRef": None,
            "active": True,
            "creationDate": "2020-05-20T15:58:31.375-05:00",
            "lastModified": "2020-05-28T13:49:16.098-05:00",
            "creator": {
                "userUid": "76543",
                "username": "user2@code42.com",
                "email": "user2@code42.com",
                "userExtRef": None,
            },
            "holdPolicyUid": "946178665645035826",
        },
    ]
}
ALL_CUSTODIANS_RESPONSE = {
    "legalHoldMemberships": [
        {
            "legalHoldMembershipUid": "99999",
            "active": True,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "123456789",
                "name": "Test legal hold matter",
            },
            "user": {
                "userUid": "840103986007089121",
                "username": "ttranda_deactivated@ttrantest.com",
                "email": "ttranda_deactivated@ttrantest.com",
                "userExtRef": None,
            },
        },
        {
            "legalHoldMembershipUid": "88888",
            "active": True,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {"legalHoldUid": "987654321", "name": "Another Matter"},
            "user": {
                "userUid": "840103986007089121",
                "username": "ttranda_deactivated@ttrantest.com",
                "email": "ttranda_deactivated@ttrantest.com",
                "userExtRef": None,
            },
        },
    ]
}


@pytest.fixture
def mock_device_settings(mocker, mock_backup_set):
    device_settings = mocker.MagicMock()
    device_settings.name = "testname"
    device_settings.guid = "1234"
    device_settings.backup_sets = [mock_backup_set, mock_backup_set]
    return device_settings


@pytest.fixture
def mock_backup_set(mocker):
    backup_set = mocker.MagicMock()
    backup_set["name"] = "test_name"
    backup_set.destinations = {"destination_guid": "destination_name"}
    backup_set.excluded_files = ["/excluded/path"]
    backup_set.included_files = ["/included/path"]
    backup_set.filename_exclusions = [".*\\.excluded_filetype"]
    backup_set.locked = True
    return backup_set


@pytest.fixture
def empty_successful_response(mocker):
    return create_mock_response(mocker)


@pytest.fixture
def device_info_response(mocker):
    return create_mock_response(mocker, data=TEST_DEVICE_RESPONSE)


def archives_list_generator():
    yield TEST_ARCHIVES_RESPONSE


def devices_list_generator():
    yield TEST_COMPUTER_PAGE


def users_list_generator():
    yield TEST_USERS_LIST_PAGE


def matter_list_generator():
    yield MATTER_RESPONSE


def custodian_list_generator():
    yield ALL_CUSTODIANS_RESPONSE


@pytest.fixture
def backupusage_response(mocker):
    return create_mock_response(mocker, data=TEST_BACKUPUSAGE_RESPONSE)


@pytest.fixture
def empty_backupusage_response(mocker):
    return create_mock_response(mocker, data=TEST_EMPTY_BACKUPUSAGE_RESPONSE)


@pytest.fixture
def device_info_success(cli_state, device_info_response):
    cli_state.sdk.devices.get_by_id.return_value = device_info_response


@pytest.fixture
def get_device_by_guid_success(cli_state, device_info_response):
    cli_state.sdk.devices.get_by_guid.return_value = device_info_response


@pytest.fixture
def archives_list_success(cli_state):
    cli_state.sdk.archive.get_all_by_device_guid.return_value = (
        archives_list_generator()
    )


@pytest.fixture
def deactivate_device_success(cli_state, empty_successful_response):
    cli_state.sdk.devices.deactivate.return_value = empty_successful_response


@pytest.fixture
def reactivate_device_success(cli_state, empty_successful_response):
    cli_state.sdk.devices.reactivate.return_value = empty_successful_response


@pytest.fixture
def deactivate_device_not_found_failure(cli_state, custom_error):
    cli_state.sdk.devices.deactivate.side_effect = Py42NotFoundError(custom_error)


@pytest.fixture
def reactivate_device_not_found_failure(cli_state, custom_error):
    cli_state.sdk.devices.reactivate.side_effect = Py42NotFoundError(custom_error)


@pytest.fixture
def deactivate_device_in_legal_hold_failure(cli_state, custom_error):
    cli_state.sdk.devices.deactivate.side_effect = Py42BadRequestError(custom_error)


@pytest.fixture
def deactivate_device_not_allowed_failure(cli_state, custom_error):
    cli_state.sdk.devices.deactivate.side_effect = Py42ForbiddenError(custom_error)


@pytest.fixture
def reactivate_device_not_allowed_failure(cli_state, custom_error):
    cli_state.sdk.devices.reactivate.side_effect = Py42ForbiddenError(custom_error)


@pytest.fixture
def backupusage_success(cli_state, backupusage_response):
    cli_state.sdk.devices.get_by_guid.return_value = backupusage_response


@pytest.fixture
def empty_backupusage_success(cli_state, empty_backupusage_response):
    cli_state.sdk.devices.get_by_guid.return_value = empty_backupusage_response


@pytest.fixture
def get_all_devices_success(cli_state):
    cli_state.sdk.devices.get_all.return_value = devices_list_generator()


@pytest.fixture
def get_all_users_success(cli_state):
    cli_state.sdk.users.get_all.return_value = users_list_generator()


@pytest.fixture
def get_all_matter_success(cli_state):
    cli_state.sdk.legalhold.get_all_matters.return_value = matter_list_generator()


@pytest.fixture
def get_all_custodian_success(cli_state):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        custodian_list_generator()
    )


@pytest.fixture
def worker_stats_factory(mocker):
    return mocker.patch(f"{_NAMESPACE}.create_worker_stats")


@pytest.fixture
def worker_stats(mocker, worker_stats_factory):
    stats = mocker.MagicMock(spec=WorkerStats)
    worker_stats_factory.return_value = stats
    return stats


def test_rename_calls_get_and_update_settings_with_expected_params(runner, cli_state):
    cli_state.sdk.devices.get_settings.return_value = mock_device_settings
    runner.invoke(
        cli,
        [
            "devices",
            "rename",
            TEST_DEVICE_GUID,
            "--new-device-name",
            TEST_NEW_DEVICE_NAME,
        ],
        obj=cli_state,
    )
    cli_state.sdk.devices.get_settings.assert_called_once_with(TEST_DEVICE_GUID)
    cli_state.sdk.devices.update_settings.assert_called_once_with(mock_device_settings)


def test_rename_when_missing_guid_prints_error(runner, cli_state):
    result = runner.invoke(
        cli, ["devices", "rename", "-n", TEST_NEW_DEVICE_NAME], obj=cli_state
    )
    assert result.exit_code == 2
    assert "Missing argument 'DEVICE_GUID'" in result.output


def test_rename_when_missing_name_prints_error(runner, cli_state):
    result = runner.invoke(cli, ["devices", "rename", TEST_DEVICE_GUID], obj=cli_state)
    assert result.exit_code == 2
    assert "Missing option '-n' / '--new-device-name'" in result.output


def test_rename_when_guid_not_found_py42_raises_exception_prints_error(
    runner, cli_state, custom_error
):
    cli_state.sdk.devices.get_settings.side_effect = Py42NotFoundError(custom_error)

    result = runner.invoke(
        cli,
        [
            "devices",
            "rename",
            TEST_DEVICE_GUID,
            "--new-device-name",
            TEST_NEW_DEVICE_NAME,
        ],
        obj=cli_state,
    )
    cli_state.sdk.devices.get_settings.assert_called_once_with(TEST_DEVICE_GUID)
    assert result.exit_code == 1
    assert (
        f"Error: The device with GUID '{TEST_DEVICE_GUID}' was not found."
        in result.output
    )


def test_deactivate_deactivates_device(
    runner, cli_state, deactivate_device_success, get_device_by_guid_success
):
    runner.invoke(cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state)
    cli_state.sdk.devices.deactivate.assert_called_once_with(TEST_DEVICE_ID)


def test_deactivate_when_given_non_guid_raises_before_making_request(runner, cli_state):
    result = runner.invoke(cli, ["devices", "deactivate", "not_a_guid"], obj=cli_state)
    assert result.exit_code == 1
    assert "Not a valid GUID." in result.output
    assert cli_state.sdk.devices.deactivate.call_count == 0


def test_deactivate_when_given_flag_updates_purge_date(
    runner,
    cli_state,
    deactivate_device_success,
    get_device_by_guid_success,
    device_info_success,
    archives_list_success,
):
    runner.invoke(
        cli,
        ["devices", "deactivate", TEST_DEVICE_GUID, "--purge-date", TEST_PURGE_DATE],
        obj=cli_state,
    )
    cli_state.sdk.archive.update_cold_storage_purge_date.assert_called_once_with(
        TEST_ARCHIVE_GUID, TEST_PURGE_DATE
    )


def test_deactivate_when_given_flag_changes_device_name(
    runner,
    cli_state,
    deactivate_device_success,
    get_device_by_guid_success,
    device_info_success,
    mock_device_settings,
):
    cli_state.sdk.devices.get_settings.return_value = mock_device_settings
    runner.invoke(
        cli,
        ["devices", "deactivate", TEST_DEVICE_GUID, "--change-device-name"],
        obj=cli_state,
    )
    assert (
        mock_device_settings.name
        == "deactivated_" + date.today().strftime("%Y-%m-%d") + "_testname"
    )
    cli_state.sdk.devices.update_settings.assert_called_once_with(mock_device_settings)


def test_deactivate_does_not_change_device_name_when_not_given_flag(
    runner,
    cli_state,
    deactivate_device_success,
    device_info_success,
    mock_device_settings,
):
    cli_state.sdk.devices.get_settings.return_value = mock_device_settings
    runner.invoke(
        cli,
        ["devices", "deactivate", TEST_DEVICE_GUID],
        obj=cli_state,
    )
    assert mock_device_settings.name == "testname"
    cli_state.sdk.devices.update_settings.assert_not_called()


def test_deactivate_fails_if_device_does_not_exist(
    runner, cli_state, deactivate_device_not_found_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert f"The device with GUID '{TEST_DEVICE_GUID}' was not found." in result.output


def test_deactivate_fails_if_device_is_on_legal_hold(
    runner, cli_state, deactivate_device_in_legal_hold_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert (
        f"The device with GUID '{TEST_DEVICE_GUID}' is in legal hold." in result.output
    )


def test_deactivate_fails_if_device_deactivation_forbidden(
    runner, cli_state, deactivate_device_not_allowed_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert (
        f"Unable to deactivate the device with GUID '{TEST_DEVICE_GUID}'."
        in result.output
    )


def test_reactivate_reactivates_device(
    runner, cli_state, deactivate_device_success, get_device_by_guid_success
):
    runner.invoke(cli, ["devices", "reactivate", TEST_DEVICE_GUID], obj=cli_state)
    cli_state.sdk.devices.reactivate.assert_called_once_with(TEST_DEVICE_ID)


def test_reactivate_fails_if_device_does_not_exist(
    runner, cli_state, reactivate_device_not_found_failure
):
    result = runner.invoke(
        cli, ["devices", "reactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert f"The device with GUID '{TEST_DEVICE_GUID}' was not found." in result.output


def test_reactivate_fails_if_device_reactivation_forbidden(
    runner, cli_state, reactivate_device_not_allowed_failure
):
    result = runner.invoke(
        cli, ["devices", "reactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert (
        f"Unable to reactivate the device with GUID '{TEST_DEVICE_GUID}'."
        in result.output
    )


def test_show_prints_device_info(runner, cli_state, backupusage_success):
    result = runner.invoke(cli, ["devices", "show", TEST_DEVICE_GUID], obj=cli_state)
    assert "SNWINTEST1" in result.output
    assert "843290890230648046" in result.output
    assert "119501" in result.output
    assert "2018-04-13T20:57:12.496Z" in result.output
    assert "6.7.1" in result.output


def test_show_prints_backup_set_info(runner, cli_state, backupusage_success):
    result = runner.invoke(cli, ["devices", "show", TEST_DEVICE_GUID], obj=cli_state)
    assert "Code42 Cloud USA West" in result.output
    assert "843293524842941560" in result.output


def test_get_device_dataframe_returns_correct_columns(
    cli_state, get_all_devices_success
):
    columns = [
        "computerId",
        "guid",
        "name",
        "osHostname",
        "status",
        "lastConnected",
        "creationDate",
        "productVersion",
        "osName",
        "osVersion",
        "userUid",
    ]
    result = _get_device_dataframe(cli_state.sdk, columns, page_size=100)
    assert "computerId" in result.columns
    assert "guid" in result.columns
    assert "name" in result.columns
    assert "osHostname" in result.columns
    assert "guid" in result.columns
    assert "status" in result.columns
    assert "lastConnected" in result.columns
    assert "creationDate" in result.columns
    assert "productVersion" in result.columns
    assert "osName" in result.columns
    assert "osVersion" in result.columns
    assert "modelInfo" not in result.columns
    assert "address" not in result.columns
    assert "buildVersion" not in result.columns


def test_device_dataframe_return_includes_backupusage_when_flag_passed(
    cli_state, get_all_devices_success
):
    result = _get_device_dataframe(
        cli_state.sdk, columns=[], page_size=100, include_backup_usage=True
    )
    assert "backupUsage" in result.columns


def test_add_usernames_to_device_dataframe_adds_usernames_to_dataframe(
    cli_state, get_all_users_success
):
    testdf = DataFrame.from_records(
        [{"userUid": "840103986007089121"}, {"userUid": "836473273124890369"}]
    )
    result = _add_usernames_to_device_dataframe(cli_state.sdk, testdf)
    assert "username" in result.columns


def test_add_legal_hold_membership_to_device_dataframe_adds_legal_hold_columns_to_dataframe(
    cli_state, get_all_matter_success, get_all_custodian_success
):
    testdf = DataFrame.from_records(
        [
            {"userUid": "840103986007089121", "status": "Active"},
            {"userUid": "836473273124890369", "status": "Active, Deauthorized"},
        ]
    )
    result = _add_legal_hold_membership_to_device_dataframe(cli_state.sdk, testdf)
    assert "legalHoldUid" in result.columns
    assert "legalHoldName" in result.columns


def test_list_without_page_size_option_defaults_to_100_results_per_page(
    cli_state, runner
):
    runner.invoke(cli, ["devices", "list"], obj=cli_state)
    cli_state.sdk.devices.get_all.assert_called_once_with(
        active=None, include_backup_usage=False, org_uid=None, page_size=100
    )


def test_list_with_page_size_option_sets_expected_page_size_in_request(
    cli_state, runner
):
    runner.invoke(cli, ["devices", "list", "--page-size", "1000"], obj=cli_state)
    cli_state.sdk.devices.get_all.assert_called_once_with(
        active=None, include_backup_usage=False, org_uid=None, page_size=1000
    )


def test_list_include_legal_hold_membership_pops_legal_hold_if_device_deactivated(
    cli_state, get_all_matter_success, get_all_custodian_success
):
    testdf = DataFrame.from_records(
        [
            {"userUid": "840103986007089121", "status": "Deactivated"},
            {"userUid": "840103986007089121", "status": "Active"},
        ]
    )

    testdf_result = DataFrame.from_records(
        [
            {
                "userUid": "840103986007089121",
                "status": "Deactivated",
                "legalHoldUid": np.nan,
                "legalHoldName": np.nan,
            },
            {
                "userUid": "840103986007089121",
                "status": "Active",
                "legalHoldUid": "123456789,987654321",
                "legalHoldName": "Test legal hold matter,Another Matter",
            },
        ]
    )
    result = _add_legal_hold_membership_to_device_dataframe(cli_state.sdk, testdf)

    assert_frame_equal(result, testdf_result)


def test_list_include_legal_hold_membership_merges_in_and_concats_legal_hold_info(
    runner,
    cli_state,
    get_all_devices_success,
    get_all_custodian_success,
    get_all_matter_success,
):
    result = runner.invoke(
        cli, ["devices", "list", "--include-legal-hold-membership"], obj=cli_state
    )

    assert "Test legal hold matter,Another Matter" in result.output
    assert "123456789,987654321" in result.output


def test_list_invalid_org_uid_raises_error(runner, cli_state, custom_error):
    custom_error.response.text = "Unable to find org"
    invalid_org_uid = "invalid_org_uid"
    cli_state.sdk.devices.get_all.side_effect = Py42OrgNotFoundError(
        custom_error, invalid_org_uid
    )
    result = runner.invoke(
        cli, ["devices", "list", "--org-uid", invalid_org_uid], obj=cli_state
    )
    assert result.exit_code == 1
    assert (
        f"Error: The organization with UID '{invalid_org_uid}' was not found."
        in result.output
    )


def test_list_excludes_recently_connected_devices_before_filtering_by_date(
    runner,
    cli_state,
    get_all_devices_success,
):
    result = runner.invoke(
        cli,
        [
            "devices",
            "list",
            "--exclude-most-recently-connected",
            "1",
            "--last-connected-before",
            TEST_DATE_NEWER,
        ],
        obj=cli_state,
    )
    assert "839648314463407622" in result.output


def test_list_backup_sets_invalid_org_uid_raises_error(runner, cli_state, custom_error):
    custom_error.response.text = "Unable to find org"
    invalid_org_uid = "invalid_org_uid"
    cli_state.sdk.devices.get_all.side_effect = Py42OrgNotFoundError(
        custom_error, invalid_org_uid
    )
    result = runner.invoke(
        cli,
        ["devices", "list-backup-sets", "--org-uid", invalid_org_uid],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        f"Error: The organization with UID '{invalid_org_uid}' was not found."
        in result.output
    )


def test_break_backup_usage_into_total_storage_correctly_calculates_values():
    test_backupusage_cell = json.loads(TEST_BACKUPUSAGE_RESPONSE)["data"]["backupUsage"]
    result = _break_backup_usage_into_total_storage(test_backupusage_cell)

    test_empty_backupusage_cell = json.loads(TEST_EMPTY_BACKUPUSAGE_RESPONSE)["data"][
        "backupUsage"
    ]
    empty_result = _break_backup_usage_into_total_storage(test_empty_backupusage_cell)

    assert_series_equal(result, Series([2, 56968051]))
    assert_series_equal(empty_result, Series([0, 0]))


def test_last_connected_after_filters_appropriate_results(
    cli_state, runner, get_all_devices_success
):
    result = runner.invoke(
        cli,
        ["devices", "list", "--last-connected-after", TEST_DATE_MIDDLE],
        obj=cli_state,
    )
    assert TEST_DATE_NEWER in result.output
    assert TEST_DATE_OLDER not in result.output


def test_last_connected_before_filters_appropriate_results(
    cli_state, runner, get_all_devices_success
):
    result = runner.invoke(
        cli,
        ["devices", "list", "--last-connected-before", TEST_DATE_MIDDLE],
        obj=cli_state,
    )
    assert TEST_DATE_NEWER not in result.output
    assert TEST_DATE_OLDER in result.output


def test_created_after_filters_appropriate_results(
    cli_state, runner, get_all_devices_success
):
    result = runner.invoke(
        cli,
        ["devices", "list", "--created-after", TEST_DATE_MIDDLE],
        obj=cli_state,
    )
    assert TEST_DATE_NEWER in result.output
    assert TEST_DATE_OLDER not in result.output


def test_created_before_filters_appropriate_results(
    cli_state, runner, get_all_devices_success
):
    result = runner.invoke(
        cli,
        ["devices", "list", "--created-before", TEST_DATE_MIDDLE],
        obj=cli_state,
    )
    assert TEST_DATE_NEWER not in result.output
    assert TEST_DATE_OLDER in result.output


def test_exclude_most_recent_connected_filters_appropriate_results(
    cli_state, runner, get_all_devices_success
):
    older_connection_guid = TEST_COMPUTER_PAGE["computers"][0]["guid"]
    newer_connection_guid = TEST_COMPUTER_PAGE["computers"][1]["guid"]
    result_1 = runner.invoke(
        cli,
        ["devices", "list", "--exclude-most-recently-connected", "1"],
        obj=cli_state,
    )
    assert older_connection_guid in result_1.output
    assert newer_connection_guid not in result_1.output

    result_2 = runner.invoke(
        cli,
        ["devices", "list", "--exclude-most-recently-connected", "2"],
        obj=cli_state,
    )
    assert older_connection_guid not in result_2.output
    assert newer_connection_guid not in result_2.output


def test_add_backup_set_settings_to_dataframe_returns_one_line_per_backup_set(
    cli_state, mock_device_settings
):
    cli_state.sdk.devices.get_settings.return_value = mock_device_settings
    testdf = DataFrame.from_records([{"guid": "1234"}])
    result = _add_backup_set_settings_to_dataframe(cli_state.sdk, testdf)
    assert len(result) == 2


def test_bulk_deactivate_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(["guid,username\n", "test,value\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "guid": "test",
            "deactivated": "False",
            "change_device_name": False,
            "purge_date": None,
        }
    ]


def test_bulk_deactivate_uses_expected_arguments_when_no_header(
    runner, mocker, cli_state
):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(["test_guid1\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "guid": "test_guid1",
            "deactivated": "False",
            "change_device_name": False,
            "purge_date": None,
        }
    ]


def test_bulk_deactivate_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(["guid,username\n", "\n", "test,value\n\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {
            "guid": "test",
            "deactivated": "False",
            "change_device_name": False,
            "purge_date": None,
        }
    ]


def test_bulk_deactivate_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats
):
    lines = ["guid\n", "1\n"]

    def _get(guid):
        if guid == "test":
            raise Exception("TEST")
        return create_mock_response(mocker, data=TEST_DEVICE_RESPONSE)

    cli_state.sdk.devices.get_by_guid.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_deactivate.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["devices", "bulk", "deactivate", "test_bulk_deactivate.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(guid="test", change_device_name="test", purge_date="test")
    handler(guid="not test", change_device_name="test", purge_date="test")
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_reactivate_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(["guid,username\n", "test,value\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [{"guid": "test", "reactivated": "False"}]


def test_bulk_reactivate_uses_expected_arguments_when_no_header(
    runner, mocker, cli_state
):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(["test_guid1\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"guid": "test_guid1", "reactivated": "False"},
    ]


def test_bulk_reactivate_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(["guid,username\n", "\n", "test,value\n\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [{"guid": "test", "reactivated": "False"}]
    bulk_processor.assert_called_once()


def test_bulk_reactivate_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats
):
    lines = ["guid\n", "1\n"]

    def _get(guid):
        if guid == "test":
            raise Exception("TEST")
        return create_mock_response(mocker, data=TEST_DEVICE_RESPONSE)

    cli_state.sdk.devices.get_by_guid.side_effect = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_reactivate.csv", "w") as csv:
            csv.writelines(lines)
        runner.invoke(
            cli,
            ["devices", "bulk", "reactivate", "test_bulk_reactivate.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(guid="test")
    handler(guid="not test")
    assert worker_stats.increment_total_errors.call_count == 1


def test_bulk_rename_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_rename.csv", "w") as csv:
            csv.writelines(["guid,name\n", "test-guid,test-name\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "rename", "test_bulk_rename.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"guid": "test-guid", "name": "test-name", "renamed": "False"}
    ]


def test_bulk_rename_ignores_blank_lines(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_rename.csv", "w") as csv:
            csv.writelines(["guid,name\n", "\n", "test-guid,test-name\n\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "rename", "test_bulk_rename.csv"],
            obj=cli_state,
        )
    assert bulk_processor.call_args[0][1] == [
        {"guid": "test-guid", "name": "test-name", "renamed": "False"}
    ]
    bulk_processor.assert_called_once()


def test_bulk_rename_uses_handler_that_when_encounters_error_increments_total_errors(
    runner, mocker, cli_state, worker_stats
):
    def _get(guid):
        if guid == "test":
            raise Exception("TEST")
        return create_mock_response(mocker, data=TEST_DEVICE_RESPONSE)

    cli_state.sdk.devices.get_settings = _get
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_bulk_rename.csv", "w") as csv:
            csv.writelines(["guid,name\n", "1,2\n"])
        runner.invoke(
            cli,
            ["devices", "bulk", "rename", "test_bulk_rename.csv"],
            obj=cli_state,
        )
    handler = bulk_processor.call_args[0][0]
    handler(guid="test", name="test-name-1")
    handler(guid="not test", name="test-name-2")
    assert worker_stats.increment_total_errors.call_count == 1
