import pytest
from datetime import datetime
from datetime import timedelta
from tests.integration import run_command


begin_date = datetime.utcnow() - timedelta(days=20)
begin_date_str = begin_date.strftime("%Y-%m-%d")


@pytest.mark.integration
@pytest.mark.parametrize(
    "command",
    [
        (
            "code42 security-data send-to localhost:5140 -p TCP -b '{}'".format(
                begin_date_str
            )
        )
    ],
)
def test_security_data_send_to(command):
    start_listener = "ncat -l 5140"
    exit_status, response = run_command(command)
    assert exit_status == 0
