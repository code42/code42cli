import pytest
from py42.exceptions import Py42DescriptionLimitExceededError
from py42.exceptions import Py42TrustedActivityConflictError
from py42.exceptions import Py42TrustedActivityIdNotFound
from py42.exceptions import Py42TrustedActivityInvalidCharacterError
from tests.conftest import create_mock_response

from code42cli.main import cli

TEST_RESOURCE_ID = 123
ALL_TRUSTED_ACTIVITIES = """
{
    "trustResources": [
        {
            "description": "test description",
            "resourceId": 456,
            "type": "DOMAIN",
            "updatedAt": "2021-09-22T15:46:35.088Z",
            "updatedByUserUid": "user123",
            "updatedByUsername": "username",
            "value": "test"
        }
    ],
    "totalCount": 10
}
"""

TRUSTED_ACTIVITY_DETAILS = """
{
  "description": "test description",
  "resourceId": 123,
  "type": "DOMAIN",
  "updatedAt": "2021-09-22T20:39:59.999Z",
  "updatedByUserUid": "user123",
  "updatedByUsername": "username",
  "value": "test"
}
"""

MISSING_ARGUMENT_ERROR = "Missing argument '{}'."
MISSING_TYPE = MISSING_ARGUMENT_ERROR.format("{DOMAIN|SLACK}")
MISSING_VALUE = MISSING_ARGUMENT_ERROR.format("VALUE")
MISSING_RESOURCE_ID_ARG = MISSING_ARGUMENT_ERROR.format("RESOURCE_ID")
RESOURCE_ID_NOT_FOUND_ERROR = "Resource ID '{}' not found."
INVALID_CHARACTER_ERROR = "Invalid character in domain or Slack workspace name"
CONFLICT_ERROR = (
    "Duplicate URL or workspace name, '{}' already exists on your trusted list."
)
DESCRIPTION_LIMIT_ERROR = "Description limit exceeded, max 250 characters allowed."


@pytest.fixture
def get_all_activities_response(mocker):
    def gen():
        yield create_mock_response(mocker, data=ALL_TRUSTED_ACTIVITIES)

    return gen()


@pytest.fixture
def trusted_activity_conflict_error(custom_error):
    return Py42TrustedActivityConflictError(custom_error, "test-case")


@pytest.fixture
def trusted_activity_description_limit_exceeded_error(custom_error):
    return Py42DescriptionLimitExceededError(custom_error)


@pytest.fixture
def trusted_activity_invalid_character_error(custom_error):
    return Py42TrustedActivityInvalidCharacterError(custom_error)


@pytest.fixture
def trusted_activity_resource_id_not_found_error(custom_error):
    return Py42TrustedActivityIdNotFound(custom_error, TEST_RESOURCE_ID)


def test_create_calls_create_with_expected_params(runner, cli_state):
    command = ["trusted-activities", "create", "DOMAIN", "test-activity"]
    runner.invoke(
        cli,
        command,
        obj=cli_state,
    )
    cli_state.sdk.trustedactivities.create.assert_called_once_with(
        "DOMAIN", "test-activity", description=None
    )


def test_create_with_optional_fields_calls_create_with_expected_params(
    runner, cli_state
):
    command = [
        "trusted-activities",
        "create",
        "SLACK",
        "test-activity",
        "--description",
        "description",
    ]
    runner.invoke(
        cli,
        command,
        obj=cli_state,
    )
    cli_state.sdk.trustedactivities.create.assert_called_once_with(
        "SLACK", "test-activity", description="description"
    )


def test_create_when_missing_type_prints_error(runner, cli_state):
    command = ["trusted-activities", "create", "--description", "description"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_TYPE in result.output


def test_create_when_missing_value_prints_error(runner, cli_state):
    command = ["trusted-activities", "create", "DOMAIN", "--description", "description"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_VALUE in result.output


def test_create_when_invalid_character_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_invalid_character_error
):
    cli_state.sdk.trustedactivities.create.side_effect = (
        trusted_activity_invalid_character_error
    )
    command = ["trusted-activities", "create", "DOMAIN", "inv@lid-domain"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert INVALID_CHARACTER_ERROR in result.output


def test_create_when_duplicate_value_conflict_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_conflict_error
):
    cli_state.sdk.trustedactivities.create.side_effect = trusted_activity_conflict_error
    command = ["trusted-activities", "create", "DOMAIN", "test-case"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert CONFLICT_ERROR.format("test-case") in result.output


def test_create_when_description_limit_exceeded_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_description_limit_exceeded_error
):
    cli_state.sdk.trustedactivities.create.side_effect = (
        trusted_activity_description_limit_exceeded_error
    )
    command = [
        "trusted-activities",
        "create",
        "DOMAIN",
        "test-domain",
        "--description",
        ">250 characters",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert DESCRIPTION_LIMIT_ERROR in result.output


def test_update_calls_update_with_expected_params(runner, cli_state):
    command = [
        "trusted-activities",
        "update",
        f"{TEST_RESOURCE_ID}",
        "--value",
        "test-activity-update",
    ]
    runner.invoke(
        cli,
        command,
        obj=cli_state,
    )
    cli_state.sdk.trustedactivities.update.assert_called_once_with(
        TEST_RESOURCE_ID,
        value="test-activity-update",
        description=None,
    )


def test_update_with_optional_fields_calls_update_with_expected_params(
    runner, cli_state
):
    command = [
        "trusted-activities",
        "update",
        f"{TEST_RESOURCE_ID}",
        "--value",
        "test-activity-update",
        "--description",
        "update description",
    ]
    runner.invoke(
        cli,
        command,
        obj=cli_state,
    )
    cli_state.sdk.trustedactivities.update.assert_called_once_with(
        TEST_RESOURCE_ID,
        value="test-activity-update",
        description="update description",
    )


def test_update_when_missing_resource_id_prints_error(runner, cli_state):
    command = ["trusted-activities", "update", "--value", "test-activity-update"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_RESOURCE_ID_ARG in result.output


def test_update_when_resource_id_not_found_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_resource_id_not_found_error
):
    cli_state.sdk.trustedactivities.update.side_effect = (
        trusted_activity_resource_id_not_found_error
    )
    command = ["trusted-activities", "update", f"{TEST_RESOURCE_ID}"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert RESOURCE_ID_NOT_FOUND_ERROR.format(TEST_RESOURCE_ID) in result.output


def test_update_when_invalid_character_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_invalid_character_error
):
    cli_state.sdk.trustedactivities.update.side_effect = (
        trusted_activity_invalid_character_error
    )
    command = [
        "trusted-activities",
        "update",
        f"{TEST_RESOURCE_ID}",
        "--value",
        "inv@lid-domain",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert INVALID_CHARACTER_ERROR in result.output


def test_update_when_duplicate_value_conflict_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_conflict_error
):
    cli_state.sdk.trustedactivities.update.side_effect = trusted_activity_conflict_error
    command = [
        "trusted-activities",
        "update",
        f"{TEST_RESOURCE_ID}",
        "--value",
        "test-case",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert CONFLICT_ERROR.format("test-case") in result.output


def test_update_when_description_limit_exceeded_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_description_limit_exceeded_error
):
    cli_state.sdk.trustedactivities.update.side_effect = (
        trusted_activity_description_limit_exceeded_error
    )
    command = [
        "trusted-activities",
        "update",
        f"{TEST_RESOURCE_ID}",
        "--description",
        ">250 characters",
    ]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert DESCRIPTION_LIMIT_ERROR in result.output


def test_remove_calls_delete_with_expected_params(runner, cli_state):
    command = ["trusted-activities", "remove", f"{TEST_RESOURCE_ID}"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.trustedactivities.delete.assert_called_once_with(TEST_RESOURCE_ID)


def test_remove_when_missing_resource_id_prints_error(runner, cli_state):
    command = ["trusted-activities", "remove"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 2
    assert MISSING_RESOURCE_ID_ARG in result.output


def test_remove_when_resource_id_not_found_py42_raises_exception_prints_error(
    runner, cli_state, trusted_activity_resource_id_not_found_error
):
    cli_state.sdk.trustedactivities.delete.side_effect = (
        trusted_activity_resource_id_not_found_error
    )
    command = ["trusted-activities", "remove", f"{TEST_RESOURCE_ID}"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert result.exit_code == 1
    assert RESOURCE_ID_NOT_FOUND_ERROR.format(TEST_RESOURCE_ID) in result.output


def test_list_calls_get_all_with_expected_params(runner, cli_state):
    command = ["trusted-activities", "list"]
    runner.invoke(cli, command, obj=cli_state)
    assert cli_state.sdk.trustedactivities.get_all.call_count == 1


def test_list_with_optional_fields_called_get_all_with_expected_params(
    runner, cli_state
):
    command = ["trusted-activities", "list", "--type", "DOMAIN"]
    runner.invoke(cli, command, obj=cli_state)
    cli_state.sdk.trustedactivities.get_all.assert_called_once_with(type="DOMAIN")


def test_list_prints_expected_data(runner, cli_state, get_all_activities_response):
    cli_state.sdk.trustedactivities.get_all.return_value = get_all_activities_response
    command = ["trusted-activities", "list"]
    result = runner.invoke(cli, command, obj=cli_state)
    assert "2021-09-22T15:46:35.088Z" in result.output
    assert "456" in result.output


def test_bulk_add_trusted_activities_uses_expected_arguments(
    runner, mocker, cli_state_with_user
):
    bulk_processor = mocker.patch("code42cli.cmds.trustedactivities.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_create.csv", "w") as csv:
            csv.writelines(
                [
                    "type,value,description\n",
                    "DOMAIN,test-domain,\n",
                    "SLACK,test-slack,desc\n",
                ]
            )
        command = ["trusted-activities", "bulk", "create", "test_create.csv"]
        runner.invoke(
            cli,
            command,
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == [
        {"type": "DOMAIN", "value": "test-domain", "description": ""},
        {"type": "SLACK", "value": "test-slack", "description": "desc"},
    ]


def test_bulk_update_trusted_activities_uses_expected_arguments(
    runner, mocker, cli_state_with_user
):
    bulk_processor = mocker.patch("code42cli.cmds.trustedactivities.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_update.csv", "w") as csv:
            csv.writelines(
                [
                    "resource_id,value,description\n",
                    "1,test-domain,\n",
                    "2,test-slack,desc\n",
                    "3,,desc\n",
                ]
            )
        command = ["trusted-activities", "bulk", "update", "test_update.csv"]
        runner.invoke(
            cli,
            command,
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == [
        {"resource_id": "1", "value": "test-domain", "description": ""},
        {"resource_id": "2", "value": "test-slack", "description": "desc"},
        {"resource_id": "3", "value": "", "description": "desc"},
    ]


def test_bulk_remove_trusted_activities_uses_expected_arguments_when_no_header(
    runner, mocker, cli_state_with_user
):
    bulk_processor = mocker.patch("code42cli.cmds.trustedactivities.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["1\n", "2\n"])
        command = ["trusted-activities", "bulk", "remove", "test_remove.csv"]
        runner.invoke(
            cli,
            command,
            obj=cli_state_with_user,
        )
    assert bulk_processor.call_args[0][1] == [
        {"resource_id": "1"},
        {"resource_id": "2"},
    ]
