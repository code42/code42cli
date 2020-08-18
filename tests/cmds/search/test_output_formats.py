from code42cli.cmds.search.output_formats import extraction_output_format
from code42cli.output_formats import to_formatted_json
from code42cli.output_formats import to_json
from code42cli.output_formats import to_table
from code42cli.output_formats import to_dynamic_csv


def test_extraction_output_format_returns_to_formatted_json_function_when_json_format_option_is_passed():
    format_function = extraction_output_format(None, None, "JSON")
    assert id(format_function) == id(to_formatted_json)


def test_extraction_output_format_returns_to_json_function_when_raw_json_format_option_is_passed():
    format_function = extraction_output_format(None, None, "RAW-JSON")
    assert id(format_function) == id(to_json)


def test_extraction_output_format_returns_to_table_function_when_ascii_table_format_option_is_passed():
    format_function = extraction_output_format(None, None, "TABLE")
    assert id(format_function) == id(to_table)


def test_extraction_output_format_returns_to_dynamic_csv_function_when_csv_format_option_is_passed():
    format_function = extraction_output_format(None, None, "CSV")
    assert id(format_function) == id(to_dynamic_csv)


def test_extraction_output_format_returns_to_table_function_when_no_format_option_is_passed():
    format_function = extraction_output_format(None, None, None)
    assert id(format_function) == id(to_table)
