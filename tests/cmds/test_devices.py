from datetime import date

import pytest
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42NotFoundError
from py42.response import Py42Response
from requests import HTTPError
from requests import Response

from code42cli.cmds.devices import _get_device_dataframe
from code42cli.main import cli

TEST_DEVICE_ID = "12345"
TEST_ARCHIVE_GUID = "954143426849296547"
TEST_PURGE_DATE = "2020-10-12"
TEST_ARCHIVES_RESPONSE = [
    {
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
]
TEST_DEVICE_RESPONSE = """{"data":{"computerId":139527,"name":"testname","osHostname":"testhostname","guid":"954143368874689941","type":"COMPUTER","status":"Active","active":true,"blocked":false,"alertState":0,"alertStates":["OK"],"userId":203988,"userUid":"938960273869958201","orgId":3099,"orgUid":"915323705751579872","computerExtRef":null,"notes":null,"parentComputerId":null,"parentComputerGuid":null,"lastConnected":"2020-10-12T16:55:40.632Z","osName":"win","osVersion":"10.0.18362","osArch":"amd64","address":"172.16.208.140:4242","remoteAddress":"72.50.201.186","javaVersion":"11.0.4","modelInfo":null,"timeZone":"America/Chicago","version":1525200006822,"productVersion":"8.2.2","buildVersion":26,"creationDate":"2020-05-14T13:03:20.302Z","modificationDate":"2020-10-12T16:55:40.632Z","loginDate":"2020-10-12T12:54:45.132Z","service":"CrashPlan"}}"""
TEST_BACKUPUSAGE_RESPONSE = """{"metadata":{"timestamp":"2020-10-13T12:51:28.410Z","params":{"incBackupUsage":"True","idType":"guid"}},"data":{"computerId":1767,"name":"SNWINTEST1","osHostname":"UNKNOWN","guid":"843290890230648046","type":"COMPUTER","status":"Active","active":true,"blocked":false,"alertState":2,"alertStates":["CriticalConnectionAlert"],"userId":1934,"userUid":"843290130258496632","orgId":1067,"orgUid":"843284512172838008","computerExtRef":null,"notes":null,"parentComputerId":null,"parentComputerGuid":null,"lastConnected":"2018-04-13T20:57:12.496Z","osName":"win","osVersion":"10.0","osArch":"amd64","address":"10.0.1.23:4242","remoteAddress":"73.53.78.104","javaVersion":"1.8.0_144","modelInfo":null,"timeZone":"America/Los_Angeles","version":1512021600671,"productVersion":"6.7.1","buildVersion":4615,"creationDate":"2018-04-10T19:23:23.564Z","modificationDate":"2018-06-29T17:41:12.616Z","loginDate":"2018-04-13T20:17:32.213Z","service":"CrashPlan","backupUsage":[{"targetComputerParentId":null,"targetComputerParentGuid":null,"targetComputerGuid":"632540230984925185","targetComputerName":"Code42 Cloud USA West","targetComputerOsName":null,"targetComputerType":"SERVER","selectedFiles":0,"selectedBytes":0,"todoFiles":0,"todoBytes":0,"archiveBytes":119501,"billableBytes":119501,"sendRateAverage":0,"completionRateAverage":0,"lastBackup":null,"lastCompletedBackup":null,"lastConnected":"2018-04-11T16:23:35.776Z","lastMaintenanceDate":"2020-10-08T21:23:12.533Z","lastCompactDate":"2020-10-08T21:23:12.411Z","modificationDate":"2020-10-12T16:19:01.267Z","creationDate":"2018-04-10T19:48:29.903Z","using":true,"alertState":16,"alertStates":["CriticalBackupAlert"],"percentComplete":0.0,"storePointId":1001,"storePointName":"cif-sea-2","serverId":1003,"serverGuid":"836476656572622471","serverName":"cif-sea","serverHostName":"https://cif-sea.crashplan.com","isProvider":false,"archiveGuid":"843293524842941560","archiveFormat":"ARCHIVE_V1","activity":{"connected":false,"backingUp":false,"restoring":false,"timeRemainingInMs":0,"remainingFiles":0,"remainingBytes":0}}]}}"""
TEST_EMPTY_BACKUPUSAGE_RESPONSE = """{"metadata":{"timestamp":"2020-10-13T12:51:28.410Z","params":{"incBackupUsage":"True","idType":"guid"}},"data":{"computerId":1767,"name":"SNWINTEST1","osHostname":"UNKNOWN","guid":"843290890230648046","type":"COMPUTER","status":"Active","active":true,"blocked":false,"alertState":2,"alertStates":["CriticalConnectionAlert"],"userId":1934,"userUid":"843290130258496632","orgId":1067,"orgUid":"843284512172838008","computerExtRef":null,"notes":null,"parentComputerId":null,"parentComputerGuid":null,"lastConnected":"2018-04-13T20:57:12.496Z","osName":"win","osVersion":"10.0","osArch":"amd64","address":"10.0.1.23:4242","remoteAddress":"73.53.78.104","javaVersion":"1.8.0_144","modelInfo":null,"timeZone":"America/Los_Angeles","version":1512021600671,"productVersion":"6.7.1","buildVersion":4615,"creationDate":"2018-04-10T19:23:23.564Z","modificationDate":"2018-06-29T17:41:12.616Z","loginDate":"2018-04-13T20:17:32.213Z","service":"CrashPlan","backupUsage":[]}}"""
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
            "userId": 1014,
            "userUid": "836473273124890369",
            "orgId": 1017,
            "orgUid": "836473214639515393",
            "computerExtRef": None,
            "notes": None,
            "parentComputerId": None,
            "parentComputerGuid": None,
            "lastConnected": "2018-03-16T17:06:50.774Z",
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
            "creationDate": "2018-03-16T16:20:00.871Z",
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
            "lastConnected": "2018-03-19T20:04:02.999Z",
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
            "creationDate": "2018-03-19T19:43:16.918Z",
            "modificationDate": "2020-09-08T15:43:45.875Z",
            "loginDate": "2018-03-19T20:03:45.360Z",
            "service": "CrashPlan",
        },
    ]
}


def _create_py42_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return Py42Response(response)


@pytest.fixture
def mock_device_settings(mocker):
    device_settings = mocker.MagicMock()
    device_settings.name = "testname"
    return device_settings


@pytest.fixture
def deactivate_response(mocker):
    return _create_py42_response(mocker, "")


@pytest.fixture
def device_info_response(mocker):
    return _create_py42_response(mocker, TEST_DEVICE_RESPONSE)


@pytest.fixture
def archives_list_generator(mocker):
    yield TEST_ARCHIVES_RESPONSE


@pytest.fixture
def devices_list_generator(mocker):
    return [TEST_COMPUTER_PAGE]


@pytest.fixture
def backupusage_response(mocker):
    return _create_py42_response(mocker, TEST_BACKUPUSAGE_RESPONSE)


@pytest.fixture
def empty_backupusage_response(mocker):
    return _create_py42_response(mocker, TEST_EMPTY_BACKUPUSAGE_RESPONSE)


@pytest.fixture
def device_info_success(cli_state, device_info_response):
    cli_state.sdk.devices.get_by_id.return_value = device_info_response


@pytest.fixture
def archives_list_success(cli_state, archives_list_generator):
    cli_state.sdk.archive.get_all_by_device_guid.return_value = archives_list_generator


@pytest.fixture
def deactivate_device_success(cli_state, deactivate_response):
    cli_state.sdk.devices.deactivate.return_value = deactivate_response


@pytest.fixture
def deactivate_device_not_found_failure(cli_state):
    cli_state.sdk.devices.deactivate.side_effect = Py42NotFoundError(HTTPError())


@pytest.fixture
def deactivate_device_in_legal_hold_failure(cli_state):
    cli_state.sdk.devices.deactivate.side_effect = Py42BadRequestError(HTTPError())


@pytest.fixture
def deactivate_device_not_allowed_failure(cli_state):
    cli_state.sdk.devices.deactivate.side_effect = Py42ForbiddenError(HTTPError())


@pytest.fixture
def backupusage_success(cli_state, backupusage_response):
    cli_state.sdk.devices.get_by_id.return_value = backupusage_response


@pytest.fixture
def empty_backupusage_success(cli_state, empty_backupusage_response):
    cli_state.sdk.devices.get_by_id.return_value = empty_backupusage_response


@pytest.fixture
def get_all_devices_success(sdk, devices_list_generator):
    sdk.devices.get_all.return_value = devices_list_generator


def test_deactivate_deactivates_device(runner, cli_state, deactivate_device_success):
    runner.invoke(
        cli, ["devices", "deactivate", "--device-id", TEST_DEVICE_ID], obj=cli_state
    )
    cli_state.sdk.devices.deactivate.assert_called_once_with(TEST_DEVICE_ID)


def test_deactivate_updates_purge_date(
    runner,
    cli_state,
    deactivate_device_success,
    device_info_success,
    archives_list_success,
):
    runner.invoke(
        cli,
        [
            "devices",
            "deactivate",
            "--device-id",
            TEST_DEVICE_ID,
            "--purge-date",
            TEST_PURGE_DATE,
        ],
        obj=cli_state,
    )
    cli_state.sdk.archive.update_cold_storage_purge_date.assert_called_once_with(
        TEST_ARCHIVE_GUID, TEST_PURGE_DATE
    )


def test_deactivate_changes_device_name(
    runner,
    cli_state,
    deactivate_device_success,
    device_info_success,
    mock_device_settings,
):
    cli_state.sdk.devices.get_settings.return_value = mock_device_settings
    runner.invoke(
        cli,
        [
            "devices",
            "deactivate",
            "--device-id",
            TEST_DEVICE_ID,
            "--change-device-name",
        ],
        obj=cli_state,
    )
    assert (
        mock_device_settings.name
        == "deactivated_" + date.today().strftime("%Y-%m-%d") + "_testname"
    )
    cli_state.sdk.devices.update_settings.assert_called_once_with(mock_device_settings)


def test_deactivate_fails_if_device_does_not_exist(
    runner, cli_state, deactivate_device_not_found_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", "--device-id", TEST_DEVICE_ID], obj=cli_state
    )
    assert result.exit_code == 1
    assert "The device {} was not found.".format(TEST_DEVICE_ID)


def test_deactivate_fails_if_device_is_on_legal_hold(
    runner, cli_state, deactivate_device_in_legal_hold_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", "--device-id", TEST_DEVICE_ID], obj=cli_state
    )
    assert result.exit_code == 1
    assert "The device {} is in legal hold.".format(TEST_DEVICE_ID)


def test_deactivate_fails_if_device_deactivation_forbidden(
    runner, cli_state, deactivate_device_not_allowed_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", "--device-id", TEST_DEVICE_ID], obj=cli_state
    )
    assert result.exit_code == 1
    assert "Unable to deactivate {}.".format(TEST_DEVICE_ID)


def test_get_info_prints_device_info(runner, cli_state, backupusage_success):
    result = runner.invoke(
        cli, ["devices", "get-info", "--device-id", TEST_DEVICE_ID], obj=cli_state
    )
    assert "SNWINTEST1" in result.output
    assert "843290890230648046" in result.output
    assert "119501" in result.output
    assert "2018-04-13T20:57:12.496Z" in result.output
    assert "6.7.1" in result.output


def test_get_info_returns_empty_values_if_no_backupusage(
    runner, cli_state, empty_backupusage_success
):
    result = runner.invoke(
        cli,
        ["devices", "get-info", "--device-id", TEST_DEVICE_ID, "-f", "json"],
        obj=cli_state,
    )
    assert '"lastBackup": null' in result.output
    assert '"archiveBytes": 0' in result.output
    assert '"lastCompletedBackup": null' in result.output


def test_get_device_dataframe_returns_correct_columns(sdk, get_all_devices_success):
    result = _get_device_dataframe(sdk)
    assert "computerId" in result.columns
    assert "guid" in result.columns
    assert "name" in result.columns
    assert "osHostname" in result.columns
    assert "guid" in result.columns
    assert "status" in result.columns
    assert "lastConnected" in result.columns
    assert "backupUsage" in result.columns
    assert "productVersion" in result.columns
    assert "osName" in result.columns
    assert "osVersion" in result.columns
    assert "modelInfo" not in result.columns
    assert "address" not in result.columns
    assert "buildVersion" not in result.columns
