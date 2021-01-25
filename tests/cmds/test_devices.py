from datetime import date

import pytest
from pandas import DataFrame
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42NotFoundError
from py42.response import Py42Response
from requests import HTTPError
from requests import Response

from code42cli import PRODUCT_NAME
from code42cli.cmds.devices import _add_backup_set_settings_to_dataframe
from code42cli.cmds.devices import _add_usernames_to_device_dataframe
from code42cli.cmds.devices import _get_device_dataframe
from code42cli.main import cli

_NAMESPACE = "{}.cmds.devices".format(PRODUCT_NAME)
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
"remainingFiles":0,"remainingBytes":0}}]}}"""
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
            "username": "qatest@code42.com",
            "email": "qatest@code42.com",
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


def _create_py42_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return Py42Response(response)


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
    return _create_py42_response(mocker, "")


@pytest.fixture
def device_info_response(mocker):
    return _create_py42_response(mocker, TEST_DEVICE_RESPONSE)


def archives_list_generator():
    yield TEST_ARCHIVES_RESPONSE


def devices_list_generator():
    yield TEST_COMPUTER_PAGE


def users_list_generator():
    yield TEST_USERS_LIST_PAGE


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
def deactivate_device_not_found_failure(cli_state):
    cli_state.sdk.devices.deactivate.side_effect = Py42NotFoundError(HTTPError())


@pytest.fixture
def reactivate_device_not_found_failure(cli_state):
    cli_state.sdk.devices.reactivate.side_effect = Py42NotFoundError(HTTPError())


@pytest.fixture
def deactivate_device_in_legal_hold_failure(cli_state):
    cli_state.sdk.devices.deactivate.side_effect = Py42BadRequestError(HTTPError())


@pytest.fixture
def deactivate_device_not_allowed_failure(cli_state):
    cli_state.sdk.devices.deactivate.side_effect = Py42ForbiddenError(HTTPError())


@pytest.fixture
def reactivate_device_not_allowed_failure(cli_state):
    cli_state.sdk.devices.reactivate.side_effect = Py42ForbiddenError(HTTPError())


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


def test_deactivate_deactivates_device(
    runner, cli_state, deactivate_device_success, get_device_by_guid_success
):
    runner.invoke(cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state)
    cli_state.sdk.devices.deactivate.assert_called_once_with(TEST_DEVICE_ID)


def test_deactivate_when_given_non_guid_raises_before_making_request(runner, cli_state):
    result = runner.invoke(cli, ["devices", "deactivate", "not_a_guid"], obj=cli_state)
    assert result.exit_code == 1
    assert "Not a valid guid." in result.output
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
        cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state,
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
    assert (
        "The device with GUID '{}' was not found.".format(TEST_DEVICE_GUID)
        in result.output
    )


def test_deactivate_fails_if_device_is_on_legal_hold(
    runner, cli_state, deactivate_device_in_legal_hold_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert (
        "The device with GUID '{}' is in legal hold.".format(TEST_DEVICE_GUID)
        in result.output
    )


def test_deactivate_fails_if_device_deactivation_forbidden(
    runner, cli_state, deactivate_device_not_allowed_failure
):
    result = runner.invoke(
        cli, ["devices", "deactivate", TEST_DEVICE_GUID], obj=cli_state
    )
    assert result.exit_code == 1
    assert (
        "Unable to deactivate the device with GUID '{}'.".format(TEST_DEVICE_GUID)
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
    result = _get_device_dataframe(cli_state.sdk, columns)
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
    result = _get_device_dataframe(cli_state.sdk, columns=[], include_backup_usage=True)
    assert "backupUsage" in result.columns


def test_add_usernames_to_device_dataframe_adds_usernames_to_dataframe(
    cli_state, get_all_users_success
):
    testdf = DataFrame.from_records(
        [{"userUid": "840103986007089121"}, {"userUid": "836473273124890369"}]
    )
    result = _add_usernames_to_device_dataframe(cli_state.sdk, testdf)
    assert "username" in result.columns


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
        cli, ["devices", "list", "--created-after", TEST_DATE_MIDDLE], obj=cli_state,
    )
    assert TEST_DATE_NEWER in result.output
    assert TEST_DATE_OLDER not in result.output


def test_created_before_filters_appropriate_results(
    cli_state, runner, get_all_devices_success
):
    result = runner.invoke(
        cli, ["devices", "list", "--created-before", TEST_DATE_MIDDLE], obj=cli_state,
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
            "deactivated": False,
            "change_device_name": False,
            "purge_date": None,
        }
    ]


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
    assert bulk_processor.call_args[0][1] == [{"guid": "test", "reactivated": False}]
