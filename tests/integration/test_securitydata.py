from datetime import datetime
from datetime import timedelta

import pytest
from tests.integration import run_command
from tests.integration.util import DataServer


begin_date = datetime.utcnow() - timedelta(days=20)
begin_date_str = begin_date.strftime("%Y-%m-%d")


@pytest.mark.integration
@pytest.mark.parametrize(
    "command,protocol",
    [
        (
            "code42 security-data send-to localhost:5140 -b '{}'".format(
                begin_date_str
            ),
            "TCP",
        ),
        (
            "code42 security-data send-to localhost:5140 -b '{}'".format(
                begin_date_str
            ),
            "UDP",
        ),
    ],
)
def test_security_data_send_to(command, protocol):
    with DataServer(protocol=protocol):
        exit_status, response = run_command(command + " -p {}".format(protocol))

    assert exit_status == 0
