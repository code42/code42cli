from datetime import datetime
from datetime import timedelta

import pytest
from tests.integration import run_command


begin_date = datetime.utcnow() - timedelta(days=20)
end_date = datetime.utcnow() - timedelta(days=10)
begin_date_str = begin_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

ALERT_SEARCH_COMMAND = "code42 alerts search -b {} -e {}".format(
    begin_date_str, end_date_str
)
ADVANCED_QUERY = """{"groupClause":"AND", "groups":[{"filterClause":"AND",
"filters":[{"operator":"ON_OR_AFTER", "term":"eventTimestamp", "value":"2020-09-13T00:00:00.000Z"},
{"operator":"ON_OR_BEFORE", "term":"eventTimestamp", "value":"2020-12-07T13:20:15.195Z"}]}],
"srtDir":"asc", "srtKey":"eventId", "pgNum":1, "pgSize":10000}
"""
ALERT_ADVANCED_QUERY_COMMAND = "code42 alerts search --advanced-query '{}'".format(
    ADVANCED_QUERY
)


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        ALERT_SEARCH_COMMAND,
        # "{} --state OPEN".format(ALERT_SEARCH_COMMAND),
        # "{} --state RESOLVED".format(ALERT_SEARCH_COMMAND),
        # "{} --actor user@code42.com".format(ALERT_SEARCH_COMMAND),
        # "{} --rule-name 'File Upload Alert'".format(ALERT_SEARCH_COMMAND),
        # "{} --rule-id 962a6a1c-54f6-4477-90bd-a08cc74cbf71".format(
        #     ALERT_SEARCH_COMMAND
        # ),
        # "{} --rule-type FedEndpointExfiltration".format(ALERT_SEARCH_COMMAND),
        # "{} --description 'Alert on any file upload'".format(ALERT_SEARCH_COMMAND),
        # "{} --exclude-rule-type 'FedEndpointExfiltration'".format(ALERT_SEARCH_COMMAND),
        # "{} --exclude-rule-id '962a6a1c-54f6-4477-90bd-a08cc74cbf71'".format(
        #     ALERT_SEARCH_COMMAND
        # ),
        # "{} --exclude-rule-name 'File Upload Alert'".format(ALERT_SEARCH_COMMAND),
        # "{} --exclude-actor-contains 'user@code42.com'".format(ALERT_SEARCH_COMMAND),
        # "{} --exclude-actor 'user@code42.com'".format(ALERT_SEARCH_COMMAND),
        # "{} --actor-contains 'user@code42.com'".format(ALERT_SEARCH_COMMAND),
        # ALERT_ADVANCED_QUERY_COMMAND,
    ],
)
def test_alert_command_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0
