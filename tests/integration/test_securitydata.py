from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful

from code42cli.main import cli

begin_date = datetime.utcnow() - timedelta(days=20)
end_date = datetime.utcnow() - timedelta(days=10)
begin_date_str = begin_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")


@pytest.mark.integration
def test_security_data_send_to_tcp_return_success_return_code(
    runner, integration_test_profile, tcp_dataserver
):
    command = append_profile(
        f"security-data send-to localhost:5140 -p TCP -b '{begin_date_str}'"
    )
    result = runner.invoke(cli, split_command(command))
    assert result.exit_code == 0


@pytest.mark.integration
def test_security_data_send_to_udp_return_success_return_code(
    runner, integration_test_profile, udp_dataserver
):
    command = append_profile(
        f"security-data send-to localhost:5141 -p UDP -b '{begin_date_str}'"
    )
    result = runner.invoke(cli, split_command(command))
    assert result.exit_code == 0


@pytest.mark.integration
def test_security_data_advanced_query_returns_success_return_code(
    runner, integration_test_profile
):
    advanced_query = """{"groupClause":"AND", "groups":[{"filterClause":"AND",
    "filters":[{"operator":"ON_OR_AFTER", "term":"eventTimestamp", "value":"2020-09-13T00:00:00.000Z"},
    {"operator":"ON_OR_BEFORE", "term":"eventTimestamp", "value":"2020-12-07T13:20:15.195Z"}]}],
    "srtDir":"asc", "srtKey":"eventId", "pgNum":1, "pgSize":10000}
    """
    command = f"security-data search --advanced-query '{advanced_query}'"
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
def test_security_data_search_command_returns_success_return_code(
    runner, integration_test_profile
):
    command = f"security-data search -b {begin_date_str} -e {end_date_str}"
    assert_test_is_successful(runner, append_profile(command))
