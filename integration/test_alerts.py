import json

import pytest
from integration import run_command
from integration.util import cleanup_after_validation

ALERT_COMMAND = "code42 alerts print -b 2020-05-18 -e 2020-05-20"


def _parse_response(response):
    return [json.loads(line) for line in response if len(line)]


def _validate_field_value(field, value, response):
    parsed_response = _parse_response(response)
    assert len(parsed_response) > 0
    for record in parsed_response:
        assert record[field] == value


@pytest.mark.parametrize(
    "command, field, value",
    [
        ("{} --state OPEN".format(ALERT_COMMAND), "state", "OPEN"),
        ("{} --state RESOLVED".format(ALERT_COMMAND), "state", "RESOLVED"),
        (
            "{} --actor spatel@code42.com".format(ALERT_COMMAND),
            "actor",
            "spatel@code42.com",
        ),
        (
            "{} --rule-name 'File Upload Alert'".format(ALERT_COMMAND),
            "name",
            "File Upload Alert",
        ),
        (
            "{} --rule-id 962a6a1c-54f6-4477-90bd-a08cc74cbf71".format(ALERT_COMMAND),
            "ruleId",
            "962a6a1c-54f6-4477-90bd-a08cc74cbf71",
        ),
        (
            "{} --rule-type FedEndpointExfiltration".format(ALERT_COMMAND),
            "type",
            "FED_ENDPOINT_EXFILTRATION",
        ),
        (
            "{} --description 'Alert on any file upload'".format(ALERT_COMMAND),
            "description",
            "Alert on any file upload events",
        ),
    ],
)
def test_alert_prints_to_stdout_and_filters_result_by_given_value(
    command, field, value
):
    return_code, response = run_command(command)
    assert return_code == 0
    _validate_field_value(field, value, response)


def _validate_begin_date(response):
    parsed_response = _parse_response(response)
    assert len(parsed_response) > 0
    for record in parsed_response:
        assert record["createdAt"].startswith("2020-05-18")


@pytest.mark.parametrize("command, validate", [(ALERT_COMMAND, _validate_begin_date)])
def test_alert_prints_to_stdout_and_filters_result_between_given_date(
    command, validate
):
    return_code, response = run_command(command)
    assert return_code == 0
    validate(response)


def _validate_severity(response):
    record = json.loads(response)
    assert record["severity"] == "MEDIUM"


@cleanup_after_validation("./integration/alerts")
def test_alert_writes_to_file_and_filters_result_by_severity():
    command = (
        "code42 alerts write-to ./integration/alerts -b 2020-05-18 -e 2020-05-20 "
        "--severity MEDIUM"
    )
    return_code, response = run_command(command)
    return _validate_severity
