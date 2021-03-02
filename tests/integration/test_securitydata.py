from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.conftest import append_profile

from code42cli.main import cli


@pytest.mark.integration
def test_security_data_send_to_tcp_return_success_return_code(
    runner, integration_test_profile, tcp_dataserver
):
    begin_date = datetime.utcnow() - timedelta(days=20)
    begin_date_str = begin_date.strftime("%Y-%m-%d")
    command = append_profile(
        f"security-data send-to localhost:5140 -p TCP -b '{begin_date_str}'"
    )
    result = runner.invoke(cli, split_command(command))
    assert result.exit_code == 0


@pytest.mark.integration
def test_security_data_send_to_udp_return_success_return_code(
    runner, integration_test_profile, udp_dataserver
):
    begin_date = datetime.utcnow() - timedelta(days=20)
    begin_date_str = begin_date.strftime("%Y-%m-%d")
    command = append_profile(
        f"security-data send-to localhost:5141 -p UDP -b '{begin_date_str}'"
    )
    result = runner.invoke(cli, split_command(command))
    assert result.exit_code == 0
