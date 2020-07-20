import pytest

from code42cli import PRODUCT_NAME
from code42cli.util import does_user_agree, find_format_width, format_string_list_to_columns, _PADDING_SIZE

TEST_HEADER = {u"key1": u"Column 1", u"key2": u"Column 10", u"key3": u"Column 100"}


@pytest.fixture
def context_with_assume_yes(mocker, cli_state):
    ctx = mocker.MagicMock()
    ctx.obj = cli_state
    cli_state.assume_yes = True
    return mocker.patch("code42cli.util.get_current_context", return_value=ctx)


@pytest.fixture
def context_without_assume_yes(mocker, cli_state):
    ctx = mocker.MagicMock()
    ctx.obj = cli_state
    cli_state.assume_yes = False
    return mocker.patch("code42cli.util.get_current_context", return_value=ctx)


_NAMESPACE = "{}.util".format(PRODUCT_NAME)


def get_expected_row_width(max_col_len, max_width):
    col_size = max_col_len + _PADDING_SIZE
    num_cols = int(max_width / col_size) or 1
    return col_size * num_cols


def test_does_user_agree_when_user_says_y_returns_true(mocker, context_without_assume_yes):
    mocker.patch("builtins.input", return_value="y")
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_capital_y_returns_true(mocker, context_without_assume_yes):
    mocker.patch("builtins.input", return_value="Y")
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_n_returns_false(mocker, context_without_assume_yes):
    mocker.patch("builtins.input", return_value="n")
    assert not does_user_agree("Test Prompt")


def test_does_user_agree_when_assume_yes_argument_passed_returns_true_and_does_not_print_prompt(
    mocker, context_with_assume_yes, capsys
):
    result = does_user_agree("Test Prompt")
    output = capsys.readouterr()
    assert result
    assert output.out == output.err == ""


def test_find_format_width_when_zero_records_sets_width_to_header_length():
    _, column_width = find_format_width([], TEST_HEADER)
    assert column_width[u"key1"] == len(TEST_HEADER[u"key1"])
    assert column_width[u"key2"] == len(TEST_HEADER[u"key2"])
    assert column_width[u"key3"] == len(TEST_HEADER[u"key3"])


def test_find_format_width_when_records_sets_width_to_greater_of_data_or_header_length():
    report = [
        {u"key1": u"test 1", u"key2": u"value xyz test", u"key3": u"test test test test"},
        {u"key1": u"1", u"key2": u"value xyz", u"key3": u"test test test test"},
    ]
    _, column_width = find_format_width(report, TEST_HEADER)
    assert column_width[u"key1"] == len(TEST_HEADER[u"key1"])
    assert column_width[u"key2"] == len(report[0][u"key2"])
    assert column_width[u"key3"] == len(report[1][u"key3"])


def test_find_format_width_filters_keys_not_present_in_header():
    report = [
        {u"key1": u"test 1", u"key2": u"value xyz test", u"key3": u"test test test test"},
        {u"key1": u"1", u"key2": u"value xyz", u"key3": u"test test test test"},
    ]
    header_with_subset_keys = {u"key1": u"Column 1", u"key3": u"Column 100"}
    result, _ = find_format_width(report, header_with_subset_keys)
    for item in result:
        assert u"key2" not in item.keys()


def test_format_string_list_to_columns_when_given_no_string_list_returns_none(mocker):
    echo = mocker.patch("code42cli.util.echo")
    format_string_list_to_columns([], None)
    format_string_list_to_columns(None, None)
    assert not echo.call_count
    

def test_format_string_list_to_columns_when_not_given_max_uses_shell_size(mocker):
    terminal_size = mocker.patch("code42cli.util.shutil.get_terminal_size")
    echo = mocker.patch("code42cli.util.echo")
    max_width = 30
    terminal_size.return_value = (max_width, None)  # Cols, Rows
    
    columns = ["col1", "col2"]
    format_string_list_to_columns(columns)
    
    printed_row = echo.call_args_list[0][0][0]
    assert len(printed_row) == get_expected_row_width(4, max_width)
    assert printed_row == "col1   col2                 "


def test_format_string_list_to_columns_when_given_small_width_prints_one_column_per_row(mocker):
    echo = mocker.patch("code42cli.util.echo")
    max_width = 5

    columns = ["col1", "col2"]
    format_string_list_to_columns(columns, max_width)

    expected_row_width = get_expected_row_width(4, max_width)
    printed_row = echo.call_args_list[0][0][0]
    assert len(printed_row) == expected_row_width
    assert printed_row == "col1   "
    
    printed_row = echo.call_args_list[1][0][0]
    assert len(printed_row) == expected_row_width
    assert printed_row == "col2   "
