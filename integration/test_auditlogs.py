from datetime import datetime
from datetime import timedelta

import pytest
from integration import run_command

SEARCH_COMMAND = "code42 audit-logs search"
BASE_COMMAND = "{} -b".format(SEARCH_COMMAND)
begin_date = datetime.utcnow() - timedelta(days=-10)
begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
end_date = datetime.utcnow() - timedelta(days=10)
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize(
    "command",
    [
        ("{} '{}'".format(BASE_COMMAND, begin_date_str)),
        ("{} '{}' -e '{}'".format(BASE_COMMAND, begin_date_str, end_date_str)),
        ("{} '{}' --end '{}'".format(BASE_COMMAND, begin_date_str, end_date_str)),
        ("{} '{}' --event-type '{}'".format(BASE_COMMAND, begin_date_str, "test")),
        ("{} '{}' --username '{}'".format(BASE_COMMAND, begin_date_str, "test")),
        ("{} '{}' --user-id '{}'".format(BASE_COMMAND, begin_date_str, "123")),
        ("{} '{}' --user-ip '{}'".format(BASE_COMMAND, begin_date_str, "0.0.0.0")),
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
def test_auditlogs_search_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0
