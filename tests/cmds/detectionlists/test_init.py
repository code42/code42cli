import pytest
from py42.response import Py42Response
from requests import Response

from code42cli.cmds.detectionlists import update_user


MOCK_USER_ID = "USER-ID"
MOCK_USER_NAME = "test@example.com"
MOCK_ALIAS = "alias@example"
MOCK_USER_PROFILE_RESPONSE = """
{{
    "type$": "USER_V2",
    "tenantId": "TENANT-ID",
    "userId": "{0}",
    "userName": "{1}",
    "displayName": "Test",
    "notes": "Notes",
    "cloudUsernames": ["{2}", "{1}"],
    "riskFactors": ["HIGH_IMPACT_EMPLOYEE"]
}}
""".format(
    MOCK_USER_ID, MOCK_USER_NAME, MOCK_ALIAS
)


@pytest.fixture
def user_response_with_cloud_aliases(mocker):
    response = mocker.MagicMock(spec=Response)
    response.text = MOCK_USER_PROFILE_RESPONSE
    return Py42Response(response)


@pytest.fixture
def mock_user_id(mocker):
    mock = mocker.patch("code42cli.cmds.detectionlists.get_user_id")
    mock.return_value = MOCK_USER_ID
    return mock


def test_update_user_when_given_cloud_alias_add_cloud_alias(
    sdk, user_response_with_cloud_aliases, mock_user_id
):
    sdk.detectionlists.get_user_by_id.return_value = user_response_with_cloud_aliases
    update_user(sdk, MOCK_USER_NAME, cloud_alias="new.alias@exaple.com")
    sdk.detectionlists.add_user_cloud_alias.assert_called_once_with(
        MOCK_USER_ID, "new.alias@exaple.com"
    )


def test_update_user_when_given_cloud_alias_first_removes_old_alias(
    sdk, user_response_with_cloud_aliases, mock_user_id
):
    sdk.detectionlists.get_user_by_id.return_value = user_response_with_cloud_aliases
    update_user(sdk, MOCK_USER_NAME, cloud_alias="new.alias@exaple.com")
    sdk.detectionlists.remove_user_cloud_alias.assert_called_once_with(
        MOCK_USER_ID, MOCK_ALIAS
    )
