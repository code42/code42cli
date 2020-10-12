from datetime import date

import pytest
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42NotFoundError
from py42.response import Py42Response
from requests import HTTPError
from requests import Response

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
def mock_today(mocker):
    mock_date = mocker.MagicMock(spec=date)
    mock_date.today.return_value = date.fromtimestamp(1602538925)  # 2020-10-12
    return mock_date


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
    mock_today,
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
    assert mock_device_settings.name == "deactivated_2020-10-12_testname"
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
