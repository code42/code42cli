import pytest

from code42cli import errors
from code42cli.cmds.util import try_get_default_header
from code42cli.output_formats import OutputFormat

key = "events"


class TestQuery:
    """"""

    pass


def search(*args, **kwargs):
    pass


def test_try_get_default_header_raises_cli_error_when_using_include_all_with_none_table_format():
    with pytest.raises(errors.Code42CLIError) as err:
        try_get_default_header(True, {}, OutputFormat.CSV)

    assert str(err.value) == "--include-all only allowed for Table output format."


def test_try_get_default_header_uses_default_header_when_not_include_all():
    default_header = {"default": "header"}
    actual = try_get_default_header(False, default_header, OutputFormat.TABLE)
    assert actual is default_header


def test_try_get_default_header_returns_none_when_is_table_and_told_to_include_all():
    default_header = {"default": "header"}
    actual = try_get_default_header(True, default_header, OutputFormat.TABLE)
    assert actual is None
