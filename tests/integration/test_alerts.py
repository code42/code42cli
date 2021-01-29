from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful
from tests.integration.util import DataServer

from code42cli.main import cli

begin_date = datetime.utcnow() - timedelta(days=20)
end_date = datetime.utcnow() - timedelta(days=10)
begin_date_str = begin_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

ALERT_SEARCH_COMMAND = "alerts search -b {} -e {}".format(begin_date_str, end_date_str)
ADVANCED_QUERY = """{"groupClause":"AND", "groups":[{"filterClause":"AND",
"filters":[{"operator":"ON_OR_AFTER", "term":"eventTimestamp", "value":"2020-09-13T00:00:00.000Z"},
{"operator":"ON_OR_BEFORE", "term":"eventTimestamp", "value":"2020-12-07T13:20:15.195Z"}]}],
"srtDir":"asc", "srtKey":"eventId", "pgNum":1, "pgSize":10000}
"""
ALERT_ADVANCED_QUERY_COMMAND = "alerts search --advanced-query '{}'".format(
    ADVANCED_QUERY
)


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        ALERT_SEARCH_COMMAND,
        "{} --state OPEN".format(ALERT_SEARCH_COMMAND),
        "{} --state RESOLVED".format(ALERT_SEARCH_COMMAND),
        "{} --actor user@code42.com".format(ALERT_SEARCH_COMMAND),
        "{} --rule-name 'File Upload Alert'".format(ALERT_SEARCH_COMMAND),
        "{} --rule-id 962a6a1c-54f6-4477-90bd-a08cc74cbf71".format(
            ALERT_SEARCH_COMMAND
        ),
        "{} --rule-type FedEndpointExfiltration".format(ALERT_SEARCH_COMMAND),
        "{} --description 'Alert on any file upload'".format(ALERT_SEARCH_COMMAND),
        "{} --exclude-rule-type 'FedEndpointExfiltration'".format(ALERT_SEARCH_COMMAND),
        "{} --exclude-rule-id '962a6a1c-54f6-4477-90bd-a08cc74cbf71'".format(
            ALERT_SEARCH_COMMAND
        ),
        "{} --exclude-rule-name 'File Upload Alert'".format(ALERT_SEARCH_COMMAND),
        "{} --exclude-actor-contains 'user@code42.com'".format(ALERT_SEARCH_COMMAND),
        "{} --exclude-actor 'user@code42.com'".format(ALERT_SEARCH_COMMAND),
        "{} --actor-contains 'user@code42.com'".format(ALERT_SEARCH_COMMAND),
        ALERT_ADVANCED_QUERY_COMMAND,
    ],
)
def test_alert_command_returns_success_return_code(
    runner, integration_test_profile, command
):
    assert_test_is_successful(runner, integration_test_profile, append_profile(command))


@pytest.mark.integration
@pytest.mark.parametrize(
    "command,protocol",
    [
        ("alerts send-to localhost:5140 -p TCP -b {}".format(begin_date_str), "TCP"),
        ("alerts send-to localhost:5140 -p UDP -b {}".format(begin_date_str), "UDP"),
    ],
)
def test_alerts_send_to(runner, integration_test_profile, command, protocol):
    with DataServer(protocol=protocol):
        result = runner.invoke(cli, split_command(append_profile(command)))
    assert result.exit_code == 0
