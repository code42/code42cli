import json

from integration import run_command
from integration.util import cleanup


def _parse_response(response):
    lines = response.split("\n")
    return [json.loads(line) for line in lines if len(line)]


def test_alert_prints_to_stdout_and_filters_result_between_given_date():
    command = "code42 alerts print -b 2020-05-18 -e 2020-05-20"
    return_code, response = run_command(command)
    assert return_code is 0
    parsed_response = _parse_response(response)
    for record in parsed_response:
        assert record["createdAt"].startswith("2020-05-18") 


def test_alert_writes_to_file_and_filters_result_by_severity():
    command = "code42 alerts write-to ./integration/alerts -b 2020-05-18 -e " \
              "2020-05-20 --severity MEDIUM"
    return_code, response = run_command(command)
    assert return_code is 0
    with cleanup("./integration/alerts") as f:
        response = f.read()
        parsed_response = _parse_response(response)
        for record in parsed_response:
            assert record["severity"] == "MEDIUM"
