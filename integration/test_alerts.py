import json
from integration import run_command


def _parse_response(response):
    result = []
    for line in response.split("\n"):
        if len(line):
            result.append(json.loads(line))
    return result


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
    with open("./integration/alerts", "r") as f:
        response = f.read()
        parsed_response = _parse_response(response)
        for record in parsed_response:
            assert record["severity"] == "MEDIUM"
    # cleanup
    run_command("rm -f ./integration/alerts")
