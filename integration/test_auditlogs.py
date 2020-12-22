from datetime import datetime
from datetime import timedelta

import pytest
from integration import run_command

BASE_COMMAND = "code42 audit-logs search -b"
begin_date = datetime.utcnow() - timedelta(days=-10)
begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize("command", [("{} '{}'".format(BASE_COMMAND, begin_date_str))])
def test_auditlogs_search(command):
    return_code, response = run_command(command)
    assert return_code == 0
