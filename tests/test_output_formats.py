import json
from collections import OrderedDict

from code42cli.output_formats import extraction_output_format
from code42cli.output_formats import get_dynamic_header
from code42cli.output_formats import output_format
from code42cli.output_formats import to_csv
from code42cli.output_formats import to_dynamic_csv
from code42cli.output_formats import to_formatted_json
from code42cli.output_formats import to_json
from code42cli.output_formats import to_table


TEST_DATA = [
    {
        "type$": "RULE_METADATA",
        "modifiedBy": "test.user+partners@code42.com",
        "modifiedAt": "2020-06-22T16:26:16.3875180Z",
        "name": "outside td",
        "description": "",
        "severity": "HIGH",
        "isSystem": False,
        "isEnabled": True,
        "ruleSource": "Alerting",
        "tenantId": "1d71796f-af5b-4231-9d8e-df6434da4663",
        "observerRuleId": "d12d54f0-5160-47a8-a48f-7d5fa5b051c5",
        "type": "FED_CLOUD_SHARE_PERMISSIONS",
        "id": "5157f1df-cb3e-4755-92a2-0f42c7841020",
        "createdBy": "test.user+partners@code42.com",
        "createdAt": "2020-06-22T16:26:16.3875180Z",
    },
    {
        "type$": "RULE_METADATA",
        "modifiedBy": "testuser@code42.com",
        "modifiedAt": "2020-07-16T08:09:44.4345110Z",
        "name": "Test different filters",
        "description": "Test different filters",
        "severity": "MEDIUM",
        "isSystem": False,
        "isEnabled": True,
        "ruleSource": "Alerting",
        "tenantId": "1d71796f-af5b-4231-9d8e-df6434da4663",
        "observerRuleId": "8b393324-c34c-44ac-9f79-4313601dd859",
        "type": "FED_ENDPOINT_EXFILTRATION",
        "id": "88354829-0958-4d60-a20d-69a53cf603b6",
        "createdBy": "test.user+partners@code42.com",
        "createdAt": "2020-05-20T11:56:41.2324240Z",
    },
    {
        "type$": "RULE_METADATA",
        "modifiedBy": "testuser@code42.com",
        "modifiedAt": "2020-05-28T16:19:19.5250970Z",
        "name": "Test Alerts using CLI",
        "description": "spatel",
        "severity": "HIGH",
        "isSystem": False,
        "isEnabled": True,
        "ruleSource": "Alerting",
        "tenantId": "1d71796f-af5b-4231-9d8e-df6434da4663",
        "observerRuleId": "5eabed1d-a406-4dfc-af81-f7485ee09b19",
        "type": "FED_ENDPOINT_EXFILTRATION",
        "id": "b2cb33e6-6683-4822-be1d-8de5ef87728e",
        "createdBy": "testuser@code42.com",
        "createdAt": "2020-05-18T11:47:16.6109560Z",
    },
]

FILTERED_OUTPUT = [
    {
        "RuleId": "d12d54f0-5160-47a8-a48f-7d5fa5b051c5",
        "Name": "outside td",
        "Severity": "HIGH",
        "Type": "FED_CLOUD_SHARE_PERMISSIONS",
        "Source": "Alerting",
        "Enabled": True,
    },
    {
        "RuleId": "8b393324-c34c-44ac-9f79-4313601dd859",
        "Name": "Test different filters",
        "Severity": "MEDIUM",
        "Type": "FED_ENDPOINT_EXFILTRATION",
        "Source": "Alerting",
        "Enabled": True,
    },
    {
        "RuleId": "5eabed1d-a406-4dfc-af81-f7485ee09b19",
        "Name": "Test Alerts using CLI",
        "Severity": "HIGH",
        "Type": "FED_ENDPOINT_EXFILTRATION",
        "Source": "Alerting",
        "Enabled": True,
    },
]

TEST_HEADER = OrderedDict()
TEST_HEADER["observerRuleId"] = "RuleId"
TEST_HEADER["name"] = "Name"
TEST_HEADER["severity"] = "Severity"
TEST_HEADER["type"] = "Type"
TEST_HEADER["ruleSource"] = "Source"
TEST_HEADER["isEnabled"] = "Enabled"


TABLE_OUTPUT = "\n".join(
    [
        """RuleId                                 Name                     Severity   Type                          Source     Enabled   """,
        """d12d54f0-5160-47a8-a48f-7d5fa5b051c5   outside td               HIGH       FED_CLOUD_SHARE_PERMISSIONS   Alerting   True      """,
        """8b393324-c34c-44ac-9f79-4313601dd859   Test different filters   MEDIUM     FED_ENDPOINT_EXFILTRATION     Alerting   True      """,
        """5eabed1d-a406-4dfc-af81-f7485ee09b19   Test Alerts using CLI    HIGH       FED_ENDPOINT_EXFILTRATION     Alerting   True      """,
    ]
)

CSV_OUTPUT = """RuleId,Name,Severity,Type,Source,Enabled
d12d54f0-5160-47a8-a48f-7d5fa5b051c5,outside td,HIGH,FED_CLOUD_SHARE_PERMISSIONS,Alerting,True
8b393324-c34c-44ac-9f79-4313601dd859,Test different filters,MEDIUM,FED_ENDPOINT_EXFILTRATION,Alerting,True
5eabed1d-a406-4dfc-af81-f7485ee09b19,Test Alerts using CLI,HIGH,FED_ENDPOINT_EXFILTRATION,Alerting,True"""


TEST_NESTED_DATA = {
    "test": "TEST",
    "name": "outside td",
    "description": "",
    "severity": "HIGH",
    "isSystem": False,
    "isEnabled": True,
    "ruleSource": ["Alerting"],
    "tenantId": "1d71796f-af5b-4231-9d8e-df6434da4663",
    "observerRuleId": {"test": ["d12d54f0-5160-47a8-a48f-7d5fa5b051c5"]},
    "type": ["FED_CLOUD_SHARE_PERMISSIONS"],
    "id": "5157f1df-cb3e-4755-92a2-0f42c7841020",
}


def test_to_csv_formats_data_to_csv_format():
    formatted_output = to_csv(TEST_DATA, TEST_HEADER)
    assert formatted_output == CSV_OUTPUT


def test_to_table_formats_data_to_table_format():
    formatted_output = to_table(TEST_DATA, TEST_HEADER)
    print(formatted_output)
    assert formatted_output == TABLE_OUTPUT


def test_to_json():
    formatted_output = to_json(TEST_DATA, TEST_HEADER)
    assert formatted_output == json.dumps(TEST_DATA)


def test_to_formatted_json():
    formatted_output = to_formatted_json(TEST_DATA, TEST_HEADER)
    assert formatted_output == json.dumps(FILTERED_OUTPUT, indent=4)


def test_output_format_returns_to_formatted_json_function_when_json_format_option_is_passed():
    format_function = output_format(None, None, "JSON")
    assert id(format_function) == id(to_formatted_json)


def test_output_format_returns_to_json_function_when_raw_json_format_option_is_passed():
    format_function = output_format(None, None, "RAW-JSON")
    assert id(format_function) == id(to_json)


def test_output_format_returns_to_table_function_when_ascii_table_format_option_is_passed():
    format_function = output_format(None, None, "TABLE")
    assert id(format_function) == id(to_table)


def test_output_format_returns_to_csv_function_when_csv_format_option_is_passed():
    format_function = output_format(None, None, "CSV")
    assert id(format_function) == id(to_csv)


def test_output_format_returns_to_table_function_when_no_format_option_is_passed():
    format_function = output_format(None, None, None)
    assert id(format_function) == id(to_table)


def test_output_format_returns_to_dynamic_csv_function_when_csv_option_is_passed():
    extraction_output_format_function = extraction_output_format(None, None, "CSV")
    assert id(extraction_output_format_function) == id(to_dynamic_csv)


def test_extraction_output_format_returns_to_formatted_json_function_when_json__option_is_passed():
    format_function = extraction_output_format(None, None, "JSON")
    assert id(format_function) == id(to_formatted_json)


def test_extraction_output_format_returns_to_json_function_when_raw_json_format_option_is_passed():
    format_function = extraction_output_format(None, None, "RAW-JSON")
    assert id(format_function) == id(to_json)


def test_get_format_header_returns_all_keys_when_include_all_is_false():
    header = get_dynamic_header(TEST_NESTED_DATA)
    assert header == {
        "test": "Test",
        "name": "Name",
        "description": "Description",
        "severity": "Severity",
        "tenantId": "Tenantid",
        "id": "Id",
    }


def test_get_format_header_returns_only_root_level_keys_when_include_all_is_true():
    header = get_dynamic_header(TEST_NESTED_DATA)
    assert header == {
        "test": "Test",
        "name": "Name",
        "description": "Description",
        "severity": "Severity",
        "isSystem": "Issystem",
        "isEnabled": "Isenabled",
        "ruleSource": "Rulesource",
        "tenantId": "Tenantid",
        "observerRuleId": "Observerruleid",
        "type": "Type",
        "id": "Id",
    }
