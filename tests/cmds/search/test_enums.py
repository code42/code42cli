from code42cli.cmds.search.enums import SecurityDataOutputFormat


def test_security_data_output_format_has_expected_options():
    options = SecurityDataOutputFormat()
    actual = list(options)
    expected = ["CEF", "CSV", "RAW-JSON", "JSON", "TABLE"]
    assert set(actual) == set(expected)
