from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import DataServer

from code42cli.main import cli


@pytest.mark.integration
def test_security_data_send_to_return_success_return_code(
    runner, integration_test_profile
):
    begin_date = datetime.utcnow() - timedelta(days=20)
    begin_date_str = begin_date.strftime("%Y-%m-%d")
    command = "security-data send-to localhost:5140 -p TCP -b {}".format(
        begin_date_str
    )
    with DataServer(protocol="TCP"):
        result = runner.invoke(cli, split_command(append_profile(command)))
    assert result.exit_code == 0
