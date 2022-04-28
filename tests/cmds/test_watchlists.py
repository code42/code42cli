import pytest

from code42cli.main import cli
from .conftest import create_mock_response

from py42.exceptions import Py42UserRiskProfileNotFound
from py42.exceptions import Py42NotFoundError
from py42.exceptions import Py42WatchlistNotFound

WATCHLISTS_RESPONSE = {
    "watchlists": [
        {
            "listType": "DEPARTING_EMPLOYEE",
            "watchlistId": "departing-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 50},
        },
        {
            "listType": "HIGH_IMPACT_EMPLOYEE",
            "watchlistId": "high-impact-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 3},
        },
        {
            "listType": "POOR_SECURITY_PRACTICES",
            "watchlistId": "poor-security-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 2},
        },
        {
            "listType": "FLIGHT_RISK",
            "watchlistId": "flight-risk-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 2},
        },
        {
            "listType": "SUSPICIOUS_SYSTEM_ACTIVITY",
            "watchlistId": "suspicious-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 2},
        },
        {
            "listType": "CONTRACT_EMPLOYEE",
            "watchlistId": "contract-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 2},
        },
        {
            "listType": "NEW_EMPLOYEE",
            "watchlistId": "new-employee-id",
            "tenantId": "tenant-123",
            "stats": {"includedUsersCount": 1},
        },
        {
            "listType": "ELEVATED_ACCESS_PRIVILEGES",
            "watchlistId": "elevated-id",
            "tenantId": "tenant-123",
            "stats": {},
        },
        {
            "listType": "PERFORMANCE_CONCERNS",
            "watchlistId": "performance-id",
            "tenantId": "tenant-123",
            "stats": {},
        },
    ],
    "totalCount": 9,
}

WATCHLISTS_INCLUDED_USERS_RESPONSE = {
    "includedUsers": [
        {
            "userId": "1234",
            "username": "one@example.com",
            "addedTime": "2022-04-10T23:05:48.096964",
        },
        {
            "userId": "2345",
            "username": "two@example.com",
            "addedTime": "2022-02-26T18:52:36.805807",
        },
        {
            "userId": "3456",
            "username": "three@example.com",
            "addedTime": "2022-02-26T18:52:36.805807",
        },
    ],
    "totalCount": 3,
}


@pytest.fixture()
def mock_watchlists_response(mocker):
    return create_mock_response(mocker, data=WATCHLISTS_RESPONSE)


@pytest.fixture()
def mock_included_users_response(mocker):
    return create_mock_response(mocker, data=WATCHLISTS_INCLUDED_USERS_RESPONSE)


class TestWatchlistsListCmd:
    def test_table_output_contains_expected_properties(
        self, runner, cli_state, mock_watchlists_response
    ):
        cli_state.sdk.watchlists.get_all.return_value = iter([mock_watchlists_response])
        res = runner.invoke(cli, ["watchlists", "list"], obj=cli_state)
        assert "listType" in res.output
        assert "watchlistId" in res.output
        assert "tenantId" in res.output
        assert "stats" in res.output
        assert "DEPARTING_EMPLOYEE" in res.output
        assert "includedUsersCount" in res.output
        assert "tenant-123" in res.output

    def test_json_output_contains_expected_properties(
        self, runner, cli_state, mock_watchlists_response
    ):
        cli_state.sdk.watchlists.get_all.return_value = iter([mock_watchlists_response])
        res = runner.invoke(cli, ["watchlists", "list", "-f", "JSON"], obj=cli_state)
        assert "listType" in res.output
        assert "watchlistId" in res.output
        assert "tenantId" in res.output
        assert "stats" in res.output
        assert "DEPARTING_EMPLOYEE" in res.output
        assert "includedUsersCount" in res.output
        assert "tenant-123" in res.output

    def test_csv_ouput_contains_expected_properties(
        self, runner, cli_state, mock_watchlists_response
    ):
        cli_state.sdk.watchlists.get_all.return_value = iter([mock_watchlists_response])
        res = runner.invoke(cli, ["watchlists", "list", "-f", "CSV"], obj=cli_state)
        assert "listType" in res.output
        assert "watchlistId" in res.output
        assert "tenantId" in res.output
        assert "stats" in res.output
        assert "DEPARTING_EMPLOYEE" in res.output
        assert "includedUsersCount" in res.output
        assert "tenant-123" in res.output


class TestWatchlistsListUsersCmd:
    def test_table_output_contains_expected_properties(
        self, runner, cli_state, mock_included_users_response
    ):
        cli_state.sdk.watchlists.get_all_included_users.return_value = iter(
            [mock_included_users_response]
        )
        res = runner.invoke(
            cli,
            ["watchlists", "list-users", "--watchlist-id", "test-id"],
            obj=cli_state,
        )
        assert "userId" in res.output
        assert "username" in res.output
        assert "addedTime" in res.output
        assert "1234" in res.output
        assert "2345" in res.output
        assert "3456" in res.output
        assert "one@example.com" in res.output
        assert "two@example.com" in res.output
        assert "three@example.com" in res.output
        assert "2022-04-10T23:05:48.096964" in res.output

    def test_json_output_contains_expected_properties(
        self, runner, cli_state, mock_included_users_response
    ):
        cli_state.sdk.watchlists.get_all_included_users.return_value = iter(
            [mock_included_users_response]
        )
        res = runner.invoke(
            cli,
            ["watchlists", "list-users", "--watchlist-id", "test-id", "-f", "JSON"],
            obj=cli_state,
        )
        assert "userId" in res.output
        assert "username" in res.output
        assert "addedTime" in res.output
        assert "1234" in res.output
        assert "2345" in res.output
        assert "3456" in res.output
        assert "one@example.com" in res.output
        assert "two@example.com" in res.output
        assert "three@example.com" in res.output
        assert "2022-04-10T23:05:48.096964" in res.output

    def test_csv_output_contains_expected_properties(
        self, runner, cli_state, mock_included_users_response
    ):
        cli_state.sdk.watchlists.get_all_included_users.return_value = iter(
            [mock_included_users_response]
        )
        res = runner.invoke(
            cli,
            ["watchlists", "list-users", "--watchlist-id", "test-id", "-f", "CSV"],
            obj=cli_state,
        )
        assert "userId" in res.output
        assert "username" in res.output
        assert "addedTime" in res.output
        assert "1234" in res.output
        assert "2345" in res.output
        assert "3456" in res.output
        assert "one@example.com" in res.output
        assert "two@example.com" in res.output
        assert "three@example.com" in res.output
        assert "2022-04-10T23:05:48.096964" in res.output

    def test_invalid_watchlist_type_raises_cli_error(self, runner, cli_state):
        res = runner.invoke(
            cli,
            ["watchlists", "list-users", "--watchlist-type", "INVALID"],
            obj=cli_state,
        )
        assert res.exit_code == 2
        assert "Invalid value for '--watchlist-type'" in res.output

    def test_missing_watchlist_identifying_option_raises_cli_error(
        self, runner, cli_state
    ):
        res = runner.invoke(
            cli,
            ["watchlists", "list-users"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: --watchlist-id OR --watchlist-type is required" in res.output


class TestWatchlistsAddCmd:
    def test_missing_watchlist_identifying_option_raises_cli_error(
        self, runner, cli_state
    ):
        res = runner.invoke(cli, ["watchlists", "add", "1234"], obj=cli_state)
        assert res.exit_code == 1
        assert "Error: --watchlist-id OR --watchlist-type is required" in res.output

    def test_invalid_watchlist_type_raises_cli_error(self, runner, cli_state):
        res = runner.invoke(
            cli,
            ["watchlists", "add", "--watchlist-type", "INVALID", "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 2
        assert "Invalid value for '--watchlist-type'" in res.output

    def test_non_int_user_arg_calls_get_by_username_and_uses_user_id(
        self, mocker, runner, cli_state
    ):
        mock_user_response = create_mock_response(mocker, data={"userId": 1234})
        cli_state.sdk.userriskprofile.get_by_username.return_value = mock_user_response
        res = runner.invoke(
            cli,
            [
                "watchlists",
                "add",
                "--watchlist-type",
                "DEPARTING_EMPLOYEE",
                "test@example.com",
            ],
            obj=cli_state,
        )
        cli_state.sdk.userriskprofile.get_by_username.assert_called_once_with(
            "test@example.com"
        )
        cli_state.sdk.watchlists.add_included_users_by_watchlist_type.assert_called_once_with(
            1234, "DEPARTING_EMPLOYEE"
        )

    def test_invalid_username_raises_not_found_cli_error(
        self, custom_error, runner, cli_state
    ):
        username = "test@example.com"
        cli_state.sdk.userriskprofile.get_by_username.side_effect = (
            Py42UserRiskProfileNotFound(custom_error, username, identifier="username")
        )
        res = runner.invoke(
            cli,
            ["watchlists", "add", "--watchlist-type", "DEPARTING_EMPLOYEE", username],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert (
            "Error: User risk profile for user with the username 'test@example.com' not found."
            in res.output
        )

    def test_invalid_user_id_raises_not_found_cli_error(
        self, custom_error, runner, cli_state
    ):
        cli_state.sdk.watchlists.add_included_users_by_watchlist_type.side_effect = (
            Py42NotFoundError(custom_error)
        )
        cli_state.sdk.watchlists.add_included_users_by_watchlist_id.side_effect = (
            Py42NotFoundError(custom_error)
        )
        res = runner.invoke(
            cli,
            ["watchlists", "add", "--watchlist-type", "DEPARTING_EMPLOYEE", "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: User ID 1234 not found." in res.output

        res = runner.invoke(
            cli,
            ["watchlists", "add", "--watchlist-id", "id", "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: User ID 1234 not found." in res.output

    def test_invalid_watchlist_id_raises_not_found_cli_error(
        self, custom_error, runner, cli_state
    ):
        invalid_watchlist_id = "INVALID"
        cli_state.sdk.watchlists.add_included_users_by_watchlist_id.side_effect = (
            Py42WatchlistNotFound(custom_error, invalid_watchlist_id)
        )
        res = runner.invoke(
            cli,
            ["watchlists", "add", "--watchlist-id", invalid_watchlist_id, "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: Watchlist ID 'INVALID' not found." in res.output


class TestWatchlistsRemoveCmd:
    def test_missing_watchlist_identifying_option_raises_cli_error(
        self, runner, cli_state
    ):
        res = runner.invoke(cli, ["watchlists", "add", "1234"], obj=cli_state)
        assert res.exit_code == 1
        assert "Error: --watchlist-id OR --watchlist-type is required" in res.output

    def test_invalid_watchlist_type_raises_cli_error(self, runner, cli_state):
        res = runner.invoke(
            cli,
            ["watchlists", "remove", "--watchlist-type", "INVALID", "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 2
        assert "Invalid value for '--watchlist-type'" in res.output

    def test_non_int_user_arg_calls_get_by_username_and_uses_user_id(
        self, mocker, runner, cli_state
    ):
        mock_user_response = create_mock_response(mocker, data={"userId": 1234})
        cli_state.sdk.userriskprofile.get_by_username.return_value = mock_user_response
        res = runner.invoke(
            cli,
            [
                "watchlists",
                "remove",
                "--watchlist-type",
                "DEPARTING_EMPLOYEE",
                "test@example.com",
            ],
            obj=cli_state,
        )
        cli_state.sdk.userriskprofile.get_by_username.assert_called_once_with(
            "test@example.com"
        )
        cli_state.sdk.watchlists.remove_included_users_by_watchlist_type.assert_called_once_with(
            1234, "DEPARTING_EMPLOYEE"
        )

    def test_invalid_username_raises_not_found_cli_error(
        self, custom_error, runner, cli_state
    ):
        username = "test@example.com"
        cli_state.sdk.userriskprofile.get_by_username.side_effect = (
            Py42UserRiskProfileNotFound(custom_error, username, identifier="username")
        )
        res = runner.invoke(
            cli,
            [
                "watchlists",
                "remove",
                "--watchlist-type",
                "DEPARTING_EMPLOYEE",
                username,
            ],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert (
            "Error: User risk profile for user with the username 'test@example.com' not found."
            in res.output
        )

    def test_invalid_user_id_raises_not_found_cli_error(
        self, custom_error, runner, cli_state
    ):
        cli_state.sdk.watchlists.remove_included_users_by_watchlist_type.side_effect = (
            Py42NotFoundError(custom_error)
        )
        cli_state.sdk.watchlists.remove_included_users_by_watchlist_id.side_effect = (
            Py42NotFoundError(custom_error)
        )
        res = runner.invoke(
            cli,
            ["watchlists", "remove", "--watchlist-type", "DEPARTING_EMPLOYEE", "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: User ID 1234 not found." in res.output

        res = runner.invoke(
            cli,
            ["watchlists", "remove", "--watchlist-id", "id", "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: User ID 1234 not found." in res.output

    def test_invalid_watchlist_id_raises_not_found_cli_error(
        self, custom_error, runner, cli_state
    ):
        invalid_watchlist_id = "INVALID"
        cli_state.sdk.watchlists.remove_included_users_by_watchlist_id.side_effect = (
            Py42WatchlistNotFound(custom_error, invalid_watchlist_id)
        )
        res = runner.invoke(
            cli,
            ["watchlists", "remove", "--watchlist-id", invalid_watchlist_id, "1234"],
            obj=cli_state,
        )
        assert res.exit_code == 1
        assert "Error: Watchlist ID 'INVALID' not found." in res.output


class TestWatchlistBulkAddCmd:
    def test_csv_without_either_username_or_user_id_raises_cli_error(
        self, runner, cli_state
    ):
        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write("watchlist_id,watchlist_type\n")
            res = runner.invoke(
                cli, ["watchlists", "bulk", "add", "csv"], obj=cli_state
            )
            assert res.exit_code == 1
            assert (
                "Error: CSV requires either a `username` or `user_id` column to identify which users to add to watchlist."
                in res.output
            )

    def test_csv_without_either_watchlist_type_or_watchlist_id_raises_cli_error(
        self, runner, cli_state
    ):
        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write("username,user_id\n")
            res = runner.invoke(
                cli, ["watchlists", "bulk", "add", "csv"], obj=cli_state
            )
            assert res.exit_code == 1
            assert (
                "Error: CSV requires either a `watchlist_id` or `watchlist_type` column to identify which watchlist to add user to."
                in res.output
            )

    def test_handle_row_when_passed_all_headers_uses_user_id_and_watchlist_id(
        self, runner, cli_state
    ):
        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write(
                    "username,user_id,watchlist_id,watchlist_type\ntest@example.com,1234,abcd,DEPARTING_EMPLOYEE\n"
                )
            res = runner.invoke(
                cli, ["watchlists", "bulk", "add", "csv"], obj=cli_state
            )
            cli_state.sdk.watchlists.add_included_users_by_watchlist_id.assert_called_once_with(
                "1234", "abcd"
            )

    def test_handle_row_when_passed_no_id_headers_uses_username_and_watchlist_type(
        self, mocker, runner, cli_state
    ):
        cli_state.sdk.userriskprofile.get_by_username.return_value = (
            create_mock_response(mocker, data={"userId": 1234})
        )

        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write(
                    "username,watchlist_type\ntest@example.com,DEPARTING_EMPLOYEE\n"
                )
            res = runner.invoke(
                cli, ["watchlists", "bulk", "add", "csv"], obj=cli_state
            )
            cli_state.sdk.watchlists.add_included_users_by_watchlist_type.assert_called_once_with(
                1234, "DEPARTING_EMPLOYEE"
            )


class TestWatchlistBulkRemoveCmd:
    def test_csv_without_either_username_or_user_id_raises_cli_error(
        self, runner, cli_state
    ):
        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write("watchlist_id,watchlist_type\n")
            res = runner.invoke(
                cli, ["watchlists", "bulk", "remove", "csv"], obj=cli_state
            )
            assert res.exit_code == 1
            assert (
                "Error: CSV requires either a `username` or `user_id` column to identify which users to remove from watchlist."
                in res.output
            )

    def test_csv_without_either_watchlist_type_or_watchlist_id_raises_cli_error(
        self, runner, cli_state
    ):
        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write("username,user_id\n")
            res = runner.invoke(
                cli, ["watchlists", "bulk", "remove", "csv"], obj=cli_state
            )
            assert res.exit_code == 1
            assert (
                "Error: CSV requires either a `watchlist_id` or `watchlist_type` column to identify which watchlist to remove user from."
                in res.output
            )

    def test_handle_row_when_passed_all_headers_uses_user_id_and_watchlist_id(
        self, runner, cli_state
    ):
        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write(
                    "username,user_id,watchlist_id,watchlist_type\ntest@example.com,1234,abcd,DEPARTING_EMPLOYEE\n"
                )
            res = runner.invoke(
                cli, ["watchlists", "bulk", "remove", "csv"], obj=cli_state
            )
            cli_state.sdk.watchlists.remove_included_users_by_watchlist_id.assert_called_once_with(
                "1234", "abcd"
            )

    def test_handle_row_when_passed_no_id_headers_uses_username_and_watchlist_type(
        self, mocker, runner, cli_state
    ):
        cli_state.sdk.userriskprofile.get_by_username.return_value = (
            create_mock_response(mocker, data={"userId": 1234})
        )

        with runner.isolated_filesystem():
            with open("csv", "w") as file:
                file.write(
                    "username,watchlist_type\ntest@example.com,DEPARTING_EMPLOYEE\n"
                )
            res = runner.invoke(
                cli, ["watchlists", "bulk", "remove", "csv"], obj=cli_state
            )
            cli_state.sdk.watchlists.remove_included_users_by_watchlist_type.assert_called_once_with(
                1234, "DEPARTING_EMPLOYEE"
            )
