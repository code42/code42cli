import json
from collections import OrderedDict

from pandas import DataFrame

import code42cli.output_formats as output_formats_module


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
        "description": "user",
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
TEST_DATAFRAME = DataFrame.from_records(TEST_DATA)


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


CSV_OUTPUT = """type$,modifiedBy,modifiedAt,name,description,severity,isSystem,isEnabled,ruleSource,tenantId,observerRuleId,type,id,createdBy,createdAt\r
RULE_METADATA,test.user+partners@code42.com,2020-06-22T16:26:16.3875180Z,outside td,,HIGH,False,True,Alerting,1d71796f-af5b-4231-9d8e-df6434da4663,d12d54f0-5160-47a8-a48f-7d5fa5b051c5,FED_CLOUD_SHARE_PERMISSIONS,5157f1df-cb3e-4755-92a2-0f42c7841020,test.user+partners@code42.com,2020-06-22T16:26:16.3875180Z\r
RULE_METADATA,testuser@code42.com,2020-07-16T08:09:44.4345110Z,Test different filters,Test different filters,MEDIUM,False,True,Alerting,1d71796f-af5b-4231-9d8e-df6434da4663,8b393324-c34c-44ac-9f79-4313601dd859,FED_ENDPOINT_EXFILTRATION,88354829-0958-4d60-a20d-69a53cf603b6,test.user+partners@code42.com,2020-05-20T11:56:41.2324240Z\r
RULE_METADATA,testuser@code42.com,2020-05-28T16:19:19.5250970Z,Test Alerts using CLI,user,HIGH,False,True,Alerting,1d71796f-af5b-4231-9d8e-df6434da4663,5eabed1d-a406-4dfc-af81-f7485ee09b19,FED_ENDPOINT_EXFILTRATION,b2cb33e6-6683-4822-be1d-8de5ef87728e,testuser@code42.com,2020-05-18T11:47:16.6109560Z\r
"""


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


def assert_csv_texts_are_equal(actual, expected):
    """Have to be careful when testing ordering because of 3.5"""
    actual = actual.replace("\r", ",")
    actual = actual.replace("\n", ",")
    expected = expected.replace("\r", ",")
    expected = expected.replace("\n", ",")
    actual = set(actual.split(","))
    expected = set(expected.split(","))
    assert actual == expected


def test_to_csv_formats_data_to_csv_format():
    formatted_output = output_formats_module.to_csv(TEST_DATA)
    assert_csv_texts_are_equal(formatted_output, CSV_OUTPUT)


def test_to_csv_when_given_no_output_returns_none():
    assert output_formats_module.to_csv(None) is None


def test_to_table_formats_data_to_table_format():
    formatted_output = output_formats_module.to_table(TEST_DATA, TEST_HEADER)
    assert formatted_output == TABLE_OUTPUT


def test_to_table_formats_when_given_no_output_returns_none():
    assert output_formats_module.to_table(None, None) is None


def test_to_table_when_not_given_header_creates_header_dynamically():
    formatted_output = output_formats_module.to_table(TEST_DATA, None)
    assert len(formatted_output) > len(TABLE_OUTPUT)
    assert "test.user+partners@code42.com" in formatted_output


def test_to_json():
    formatted_output = output_formats_module.to_json(TEST_DATA)
    assert formatted_output == "{}\n".format(json.dumps(TEST_DATA))


def test_to_formatted_json():
    formatted_output = output_formats_module.to_formatted_json(TEST_DATA)
    assert formatted_output == "{}\n".format(json.dumps(TEST_DATA, indent=4))


class TestOutputFormatter:
    def test_init_sets_format_func_to_formatted_json_function_when_json_format_option_is_passed(
        self, mock_to_json
    ):
        output_format = output_formats_module.OutputFormat.RAW
        formatter = output_formats_module.OutputFormatter(output_format)
        for _ in formatter.get_formatted_output([{"TEST": "FOOBAR"}]):
            pass
        mock_to_json.assert_called_once_with({"TEST": "FOOBAR"})

    def test_init_sets_format_func_to_json_function_when_raw_json_format_option_is_passed(
        self, mock_to_formatted_json
    ):
        output_format = output_formats_module.OutputFormat.JSON
        formatter = output_formats_module.OutputFormatter(output_format)
        for _ in formatter.get_formatted_output(["TEST"]):
            pass
        mock_to_formatted_json.assert_called_once_with("TEST")

    def test_init_sets_format_func_to_table_function_when_table_format_option_is_passed(
        self, mock_to_table
    ):
        output_format = output_formats_module.OutputFormat.TABLE
        formatter = output_formats_module.OutputFormatter(output_format)
        for _ in formatter.get_formatted_output("TEST"):
            pass
        mock_to_table.assert_called_once_with("TEST", None)

    def test_init_sets_format_func_to_csv_function_when_csv_format_option_is_passed(
        self, mock_to_csv
    ):
        output_format = output_formats_module.OutputFormat.CSV
        formatter = output_formats_module.OutputFormatter(output_format)
        for _ in formatter.get_formatted_output("TEST"):
            pass
        mock_to_csv.assert_called_once_with("TEST")

    def test_init_sets_format_func_to_table_function_when_no_format_option_is_passed(
        self, mock_to_table
    ):
        formatter = output_formats_module.OutputFormatter(None)
        for _ in formatter.get_formatted_output("TEST"):
            pass
        mock_to_table.assert_called_once_with("TEST", None)


class TestDataFrameOutputFormatter:
    def test_init_sets_format_func_to_formatted_json_function_when_json_format_option_is_passed(
        self, mock_dataframe_to_json
    ):
        output_format = output_formats_module.OutputFormat.RAW
        formatter = output_formats_module.DataFrameOutputFormatter(output_format)
        formatter.echo_formatted_dataframe(TEST_DATAFRAME)
        mock_dataframe_to_json.assert_called_once_with(
            TEST_DATAFRAME, orient="records", lines=False, index=False
        )

    def test_init_sets_format_func_to_json_function_when_raw_json_format_option_is_passed(
        self, mock_dataframe_to_json
    ):
        output_format = output_formats_module.OutputFormat.JSON
        formatter = output_formats_module.DataFrameOutputFormatter(output_format)
        formatter.echo_formatted_dataframe(TEST_DATAFRAME)
        mock_dataframe_to_json.assert_called_once_with(
            TEST_DATAFRAME, orient="records", lines=True, index=False
        )

    def test_init_sets_format_func_to_table_function_when_table_format_option_is_passed(
        self, mock_dataframe_to_string
    ):
        output_format = output_formats_module.OutputFormat.TABLE
        formatter = output_formats_module.DataFrameOutputFormatter(output_format)
        formatter.echo_formatted_dataframe(TEST_DATAFRAME)
        mock_dataframe_to_string.assert_called_once_with(TEST_DATAFRAME, index=False)

    def test_init_sets_format_func_to_csv_function_when_csv_format_option_is_passed(
        self, mock_dataframe_to_csv
    ):
        output_format = output_formats_module.OutputFormat.CSV
        formatter = output_formats_module.DataFrameOutputFormatter(output_format)
        formatter.echo_formatted_dataframe(TEST_DATAFRAME)
        mock_dataframe_to_csv.assert_called_once_with(TEST_DATAFRAME, index=False)

    def test_init_sets_format_func_to_table_function_when_no_format_option_is_passed(
        self, mock_dataframe_to_string
    ):
        formatter = output_formats_module.DataFrameOutputFormatter(None)
        formatter.echo_formatted_dataframe(TEST_DATAFRAME)
        mock_dataframe_to_string.assert_called_once_with(TEST_DATAFRAME, index=False)
