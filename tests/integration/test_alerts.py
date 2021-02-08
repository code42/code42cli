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


@pytest.mark.integration
def test_alerts_search_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = "alerts search -b {} -e {}".format(begin_date_str, end_date_str)
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
@pytest.mark.parametrize(
    "protocol", ["TCP", "UDP"],
)
def test_alerts_send_to_returns_success_return_code(
    runner, integration_test_profile, protocol
):
    command = "alerts send-to localhost:5140 -p {} -b {}".format(
        protocol, begin_date_str
    )
    with DataServer(protocol=protocol):
        result = runner.invoke(cli, split_command(append_profile(command)))
    assert result.exit_code == 0


@pytest.mark.integration
def test_alerts_advanced_query_returns_success_return_code(
    runner, integration_test_profile
):
    ADVANCED_QUERY = """{"groupClause":"AND", "groups":[{"filterClause":"AND",
    "filters":[{"operator":"ON_OR_AFTER", "term":"eventTimestamp", "value":"2020-09-13T00:00:00.000Z"},
    {"operator":"ON_OR_BEFORE", "term":"eventTimestamp", "value":"2020-12-07T13:20:15.195Z"}]}],
    "srtDir":"asc", "srtKey":"eventId", "pgNum":1, "pgSize":10000}
    """
    command = "alerts search --advanced-query '{}'".format(ADVANCED_QUERY)
    assert_test_is_successful(runner, append_profile(command))
