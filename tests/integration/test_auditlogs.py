from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import assert_test_is_successful

from code42cli.main import cli


begin_date = datetime.utcnow() - timedelta(days=2)
begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
end_date = datetime.utcnow() - timedelta(days=0)
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.integration
<<<<<<< HEAD
@pytest.mark.parametrize(
    "protocol", ["UDP", "TCP"],
)
def test_auditlogs_send_to_command_returns_success_return_code(
    runner, integration_test_profile, protocol
):
    command = f"audit-logs send-to localhost:5140 -p {protocol} -b '{begin_date_str}'"
    with DataServer(protocol=protocol):
        result = runner.invoke(cli, split_command(append_profile(command)))
=======
def test_auditlogs_send_to_tcp_command_returns_success_return_code(
    runner, integration_test_profile, tcp_dataserver
):
    command = append_profile(
        f"audit-logs send-to localhost:5140 -p TCP -b '{begin_date_str}'"
    )
    result = runner.invoke(cli, split_command(command))
    assert result.exit_code == 0


@pytest.mark.integration
def test_auditlogs_send_to_udp_command_returns_success_return_code(
    runner, integration_test_profile, udp_dataserver
):
    command = append_profile(
        f"audit-logs send-to localhost:5141 -p UDP -b '{begin_date_str}'"
    )
    result = runner.invoke(cli, split_command(command))
>>>>>>> master
    assert result.exit_code == 0


@pytest.mark.integration
def test_auditlogs_search_command_with_short_hand_begin_returns_success_return_code(
    runner, integration_test_profile
):
    command = "audit-logs search -b '{}'".format(begin_date_str)
    assert_test_is_successful(runner, append_profile(command))


@pytest.mark.integration
def test_auditlogs_search_command_with_full_begin_returns_success_return_code(
    runner, integration_test_profile,
):
    command = "audit-logs search --begin '{}'".format(begin_date_str)
    assert_test_is_successful(runner, append_profile(command))
