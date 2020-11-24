from datetime import datetime
from datetime import timedelta

from integration import run_command

BASE_COMMAND = "code42 auditlogs search -b"


def test_auditlogs_search():
    begin_date = datetime.utcnow() - timedelta(days=-10)
    begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
    return_code, response = run_command(BASE_COMMAND + begin_date_str)
    assert return_code == 0
