from datetime import datetime
from datetime import timedelta
from shlex import split as split_command

import pytest
from tests.integration.conftest import append_profile
from tests.integration.util import DataServer

from code42cli.main import cli


begin_date = datetime.utcnow() - timedelta(days=20)
begin_date_str = begin_date.strftime("%Y-%m-%d")


@pytest.mark.integration
@pytest.mark.parametrize(
    "command,protocol",
    [
        (
            "security-data send-to localhost:5140 -p TCP -b {}".format(begin_date_str),
            "TCP",
        ),
        (
            "security-data send-to localhost:5140 -p UDP -b {}".format(begin_date_str),
            "UDP",
        ),
    ],
)
def test_security_data_send_to(runner, integration_test_profile, command, protocol):
    with DataServer(protocol=protocol):
        result = runner.invoke(
            cli, split_command(append_profile(command)), obj=integration_test_profile
        )
    assert result.exit_code == 0
