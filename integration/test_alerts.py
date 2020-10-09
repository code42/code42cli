from datetime import datetime
from datetime import timedelta

import pytest
from integration import run_command


begin_date = datetime.utcnow() - timedelta(days=20)
end_date = datetime.utcnow() - timedelta(days=10)
begin_date_str = begin_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

ALERT_COMMAND = "code42 alerts search -b {} -e {}".format(begin_date_str, end_date_str)


@pytest.mark.parametrize(
    "command",
    [
        ("{}".format(ALERT_COMMAND)),
        ("{} --state OPEN".format(ALERT_COMMAND)),
        ("{} --state RESOLVED".format(ALERT_COMMAND)),
        ("{} --actor user@code42.com".format(ALERT_COMMAND)),
        ("{} --rule-name 'File Upload Alert'".format(ALERT_COMMAND)),
        ("{} --rule-id 962a6a1c-54f6-4477-90bd-a08cc74cbf71".format(ALERT_COMMAND)),
        ("{} --rule-type FedEndpointExfiltration".format(ALERT_COMMAND)),
        ("{} --description 'Alert on any file upload'".format(ALERT_COMMAND)),
    ],
)
def test_alert_returns_success_return_code(command):
    return_code, response = run_command(command)
    assert return_code == 0
