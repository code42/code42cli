from datetime import datetime
from datetime import timedelta

import pytest
from integration import run_command

SEARCH_COMMAND = "code42 audit-logs search"
BASE_COMMAND = "{0} -b".format(SEARCH_COMMAND)
begin_date = datetime.utcnow() - timedelta(days=-10)
begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
end_date = datetime.utcnow() - timedelta(days=10)
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize(
    "command",
    [
        ("{0} '{1}'".format(BASE_COMMAND, begin_date_str)),
        ("{0} '{1}' -e '{2}'".format(BASE_COMMAND, begin_date_str, end_date_str)),
        ("{0} '{1}' --end '{2}'".format(BASE_COMMAND, begin_date_str, end_date_str)),
        ("{0} '{1}' --event-type '{2}'".format(BASE_COMMAND, begin_date_str, "test")),
        ("{0} '{1}' --username '{2}'".format(BASE_COMMAND, begin_date_str, "test")),
        ("{0} '{1}' --user-id '{2}'".format(BASE_COMMAND, begin_date_str, "123")),
        ("{0} '{1}' --user-ip '{2}'".format(BASE_COMMAND, begin_date_str, "0.0.0.0")),
        ("{0} '{1}' --affected-user-id '{2}'".format(BASE_COMMAND, begin_date_str, "123")),
        ("{0} '{1}' --affected-username '{2}'".format(BASE_COMMAND, begin_date_str, "test")),
        ("{0} '{1}' -f {2}".format(BASE_COMMAND, begin_date_str, "CSV")),
        ("{0} '{1}' -f '{2}'".format(BASE_COMMAND, begin_date_str, "TABLE")),
        ("{0} '{1}' -f '{2}'".format(BASE_COMMAND, begin_date_str, "JSON")),
        ("{0} '{1}' -f '{2}'".format(BASE_COMMAND, begin_date_str, "RAW-JSON")),
        ("{0} --begin '{1}' -f '{2}'".format(SEARCH_COMMAND, begin_date_str, "RAW-JSON")),
        ("{0} '{1}' -d".format(BASE_COMMAND, begin_date_str)),
        ("{0} '{1}' --debug".format(BASE_COMMAND, begin_date_str)),
    ]
)
def test_auditlogs_search(command):
    return_code, response = run_command(command)
    assert return_code == 0
