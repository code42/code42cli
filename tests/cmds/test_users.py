import json

import pytest
from pandas.core.frame import DataFrame
from py42.response import Py42Response
from requests import Response

from code42cli.cmds.users import _get_role_id
from code42cli.cmds.users import _get_users_dataframe
from code42cli.main import cli

TEST_ROLE_RETURN_DATA = {"data": [{"roleName": "Customer Cloud Admin", "roleId": "12"}]}

TEST_USERS_RESPONSE = {
    "users": [
        {
            "userId": 1234,
            "userUid": "997962681513153325",
            "status": "Active",
            "username": "test_username@code42.com",
            "creationDate": "2021-03-12T20:07:40.898Z",
            "modificationDate": "2021-03-12T20:07:40.938Z",
        }
    ]
}


def _create_py42_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return Py42Response(response)


def get_all_users_generator():
    yield TEST_USERS_RESPONSE


@pytest.fixture
def get_available_roles_response(mocker):
    return _create_py42_response(mocker, json.dumps(TEST_ROLE_RETURN_DATA))


@pytest.fixture
def get_all_users_success(cli_state):
    cli_state.sdk.users.get_all.return_value = get_all_users_generator()


@pytest.fixture
def get_available_roles_success(cli_state, get_available_roles_response):
    cli_state.sdk.users.get_available_roles.return_value = get_available_roles_response


def test_list_outputs_appropriate_columns(runner, cli_state, get_all_users_success):
    result = runner.invoke(cli, ["users", "list"], obj=cli_state)
    assert "userId" in result.output
    assert "userUid" in result.output
    assert "status" in result.output
    assert "username" in result.output
    assert "creationDate" in result.output
    assert "modificationDate" in result.output


def test_get_role_id_returns_appropriate_role_id(
    cli_state, get_available_roles_success
):
    result = _get_role_id(cli_state.sdk, "Customer Cloud Admin")
    assert result == "12"


def test_get_users_dataframe_returns_dataframe(cli_state, get_all_users_success):
    result = _get_users_dataframe(
        cli_state.sdk, org_uid=None, role_id=None, active=None
    )
    assert isinstance(result, DataFrame)


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
