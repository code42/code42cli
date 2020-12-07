from datetime import datetime
from datetime import timedelta

import pytest
from integration import run_command


begin_date = datetime.utcnow() - timedelta(days=20)
end_date = datetime.utcnow() - timedelta(days=10)
begin_date_str = begin_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

ALERT_COMMAND = "code42 alerts search -b {} -e {}".format(begin_date_str, end_date_str)
ADVANCED_QUERY = """{"groupClause":"AND", "groups":[{"filterClause":"AND", 
"filters":[{"operator":"ON_OR_AFTER", "term":"eventTimestamp", "value":"2020-09-13T00:00:00.000Z"},
{"operator":"ON_OR_BEFORE", "term":"eventTimestamp", "value":"2020-12-07T13:20:15.195Z"}]}], 
"srtDir":"asc", "srtKey":"eventId", "pgNum":1, "pgSize":10000}
"""
ALERT_ADVANCED_QUERY_COMMAND = f"code42 alerts search --advanced-query '{ADVANCED_QUERY}'"


@pytest.mark.parametrize(
    "command",
    [
        f"{ALERT_COMMAND}",
        f"{ALERT_COMMAND} --state OPEN",
        f"{ALERT_COMMAND} --state RESOLVED",
        f"{ALERT_COMMAND} --actor user@code42.com",
        f"{ALERT_COMMAND} --rule-name 'File Upload Alert'",
        f"{ALERT_COMMAND} --rule-id 962a6a1c-54f6-4477-90bd-a08cc74cbf71",
        f"{ALERT_COMMAND} --rule-type FedEndpointExfiltration",
        f"{ALERT_COMMAND} --description 'Alert on any file upload'",
        f"{ALERT_COMMAND} --exclude-rule-type 'FedEndpointExfiltration'",
        f"{ALERT_COMMAND} --exclude-rule-id '962a6a1c-54f6-4477-90bd-a08cc74cbf71'",
        f"{ALERT_COMMAND} --exclude-rule-name 'File Upload Alert'",
        f"{ALERT_COMMAND} --exclude-actor-contains 'user@code42.com'",
        f"{ALERT_COMMAND} --exclude-actor 'user@code42.com'",
        f"{ALERT_COMMAND} --actor-contains 'user@code42.com'",
        ALERT_ADVANCED_QUERY_COMMAND,
    ],
)
def test_alert_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0


@pytest.mark.parametrize(
    "command",
    [
        f"{ALERT_COMMAND} --advanced-query '{ADVANCED_QUERY}'",
    ]
)
def test_begin_cant_be_used_with_advanced_query(command):
    return_code, response = run_command(command)
    assert return_code == 2
    assert "--begin can't be used with: --advanced-query" in response[0]
