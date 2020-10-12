import pytest
from py42.exceptions import Py42BadRequestError, Py42ForbiddenError, Py42NotFoundError
from py42.response import Py42Response
from requests import HTTPError
from requests import Response

from code42cli.main import cli

TEST_DEVICE_ID = "12345"

def _create_py42_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return Py42Response(response)

@pytest.fixture
def deactivate_response(mocker):
	return _create_py42_response(mocker, "")

@pytest.fixture
def deactivate_device_success(cli_state):
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
	result = runner.invoke(
		cli,
		[
			"devices",
			"deactivate",
			"--device-id",
			TEST_DEVICE_ID
		],
		obj=cli_state
	)
	cli_state.sdk.devices.deactivate.assert_called_once_with(TEST_DEVICE_ID)


def test_deactivate_fails_if_device_does_not_exist(runner, cli_state, deactivate_device_not_found_failure):
	result = runner.invoke(
		cli,
		[
			"devices",
			"deactivate",
			"--device-id",
			TEST_DEVICE_ID
		],
		obj=cli_state
	)
	assert result.exit_code == 1
	assert ("The device {} was not found.".format(TEST_DEVICE_ID))

def test_deactivate_fails_if_device_is_on_legal_hold(runner, cli_state, deactivate_device_in_legal_hold_failure):
	result = runner.invoke(
		cli,
		[
			"devices",
			"deactivate",
			"--device-id",
			TEST_DEVICE_ID
		],
		obj=cli_state
	)
	assert result.exit_code == 1
	assert ("The device {} is in legal hold.".format(TEST_DEVICE_ID))

def test_deactivate_fails_if_device_deactivation_forbidden(runner, cli_state, deactivate_device_not_allowed_failure):
	result = runner.invoke(
		cli,
		[
			"devices",
			"deactivate",
			"--device-id",
			TEST_DEVICE_ID
		],
		obj=cli_state
	)
	assert result.exit_code == 1
	assert ("Unable to deactivate {}.".format(TEST_DEVICE_ID))