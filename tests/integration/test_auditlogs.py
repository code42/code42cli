from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.util import assert_test_is_successful
from tests.integration.util import DataServer

from code42cli.main import cli


SEARCH_COMMAND = "audit-logs search"
BASE_COMMAND = "{} -b".format(SEARCH_COMMAND)
begin_date = datetime.utcnow() - timedelta(days=2)
begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
end_date = datetime.utcnow() - timedelta(days=0)
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.integration
@pytest.mark.parametrize(
    "command,protocol",
    [
        (
            "audit-logs send-to localhost:5140 -p TCP -b '{}'".format(begin_date_str),
            "TCP",
        ),
        (
            "audit-logs send-to localhost:5140 -p UDP -b '{}'".format(begin_date_str),
            "UDP",
        ),
    ],
)
def test_auditlogs_send_to(runner, integration_test_profile, command, protocol):
    with DataServer(protocol=protocol):
        result = runner.invoke(
            cli, split_command(command), obj=integration_test_profile
        )
    assert result.exit_code == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        ("{} '{}'".format(BASE_COMMAND, begin_date_str)),
        ("{} '{}' -e '{}'".format(BASE_COMMAND, begin_date_str, end_date_str)),
        ("{} '{}' --end '{}'".format(BASE_COMMAND, begin_date_str, end_date_str)),
        ("{} '{}' --event-type '{}'".format(BASE_COMMAND, begin_date_str, "test")),
        ("{} '{}' --actor-ip '{}'".format(BASE_COMMAND, begin_date_str, "0.0.0.0")),
        ("{} '{}' --affected-user-id '{}'".format(BASE_COMMAND, begin_date_str, "123")),
        (
            "{} '{}' --affected-username '{}'".format(
                BASE_COMMAND, begin_date_str, "test"
            )
        ),
        ("{} '{}' -f {}".format(BASE_COMMAND, begin_date_str, "CSV")),
        ("{} '{}' -f '{}'".format(BASE_COMMAND, begin_date_str, "TABLE")),
        ("{} '{}' -f '{}'".format(BASE_COMMAND, begin_date_str, "JSON")),
        ("{} '{}' -f '{}'".format(BASE_COMMAND, begin_date_str, "RAW-JSON")),
        ("{} '{}' --format {}".format(BASE_COMMAND, begin_date_str, "CSV")),
        ("{} '{}' --format '{}'".format(BASE_COMMAND, begin_date_str, "TABLE")),
        ("{} '{}' --format '{}'".format(BASE_COMMAND, begin_date_str, "JSON")),
        ("{} '{}' --format '{}'".format(BASE_COMMAND, begin_date_str, "RAW-JSON")),
        ("{} --begin '{}'".format(SEARCH_COMMAND, begin_date_str)),
        ("{} '{}' -d".format(BASE_COMMAND, begin_date_str)),
        ("{} '{}' --debug".format(BASE_COMMAND, begin_date_str)),
    ],
)
def test_auditlogs_search_command_returns_success_return_code(
    runner, integration_test_profile, command
):
    assert_test_is_successful(runner, integration_test_profile, command)
