import pytest

from code42cli.util import _PADDING_SIZE
from code42cli.util import does_user_agree
from code42cli.util import find_format_width
from code42cli.util import format_string_list_to_columns
from code42cli.util import get_url_parts

TEST_HEADER = {"key1": "Column 1", "key2": "Column 10", "key3": "Column 100"}


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


@pytest.fixture
def echo_output(mocker):
    return mocker.patch("code42cli.util.echo")


_NAMESPACE = "code42cli.util"


def get_expected_row_width(max_col_len, max_width):
    col_size = max_col_len + _PADDING_SIZE
    num_cols = int(max_width / col_size) or 1
    return col_size * num_cols


def test_does_user_agree_when_user_says_y_returns_true(
    mocker, context_without_assume_yes
):
    mocker.patch("builtins.input", return_value="y")
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_capital_y_returns_true(
    mocker, context_without_assume_yes
):
    mocker.patch("builtins.input", return_value="Y")
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_n_returns_false(
    mocker, context_without_assume_yes
):
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
    assert column_width["key1"] == len(TEST_HEADER["key1"])
    assert column_width["key2"] == len(TEST_HEADER["key2"])
    assert column_width["key3"] == len(TEST_HEADER["key3"])


def test_find_format_width_when_records_sets_width_to_greater_of_data_or_header_length():
    report = [
        {"key1": "test 1", "key2": "value xyz test", "key3": "test test test test"},
        {"key1": "1", "key2": "value xyz", "key3": "test test test test"},
    ]
    _, column_width = find_format_width(report, TEST_HEADER)
    assert column_width["key1"] == len(TEST_HEADER["key1"])
    assert column_width["key2"] == len(report[0]["key2"])
    assert column_width["key3"] == len(report[1]["key3"])


def test_find_format_width_filters_keys_not_present_in_header():
    report = [
        {"key1": "test 1", "key2": "value xyz test", "key3": "test test test test"},
        {"key1": "1", "key2": "value xyz", "key3": "test test test test"},
    ]
    header_with_subset_keys = {"key1": "Column 1", "key3": "Column 100"}
    result, _ = find_format_width(report, header_with_subset_keys)
    for item in result:
        assert "key2" not in item.keys()


def test_format_string_list_to_columns_when_given_no_string_list_does_not_echo(
    echo_output,
):
    format_string_list_to_columns([], None)
    format_string_list_to_columns(None, None)
    assert not echo_output.call_count


def test_format_string_list_to_columns_when_not_given_max_uses_shell_size(
    mocker, echo_output
):
    terminal_size = mocker.patch("code42cli.util.shutil.get_terminal_size")
    max_width = 30
    terminal_size.return_value = (max_width, None)  # Cols, Rows

    columns = ["col1", "col2"]
    format_string_list_to_columns(columns)

    printed_row = echo_output.call_args_list[0][0][0]
    assert len(printed_row) == get_expected_row_width(4, max_width)
    assert printed_row == "col1   col2                 "


def test_format_string_list_to_columns_when_given_small_max_width_prints_one_column_per_row(
    echo_output,
):
    max_width = 5

    columns = ["col1", "col2"]
    format_string_list_to_columns(columns, max_width)

    expected_row_width = get_expected_row_width(4, max_width)
    printed_row = echo_output.call_args_list[0][0][0]
    assert len(printed_row) == expected_row_width
    assert printed_row == "col1   "

    printed_row = echo_output.call_args_list[1][0][0]
    assert len(printed_row) == expected_row_width
    assert printed_row == "col2   "


def test_format_string_list_to_columns_uses_width_of_longest_string(echo_output):
    max_width = 5

    columns = ["col1", "col2_that_is_really_long"]
    format_string_list_to_columns(columns, max_width)

    expected_row_width = get_expected_row_width(
        len("col2_that_is_really_long"), max_width
    )
    printed_row = echo_output.call_args_list[0][0][0]
    assert len(printed_row) == expected_row_width
    assert printed_row == "col1                       "

    printed_row = echo_output.call_args_list[1][0][0]
    assert len(printed_row) == expected_row_width
    assert printed_row == "col2_that_is_really_long   "


def test_url_parts():
    server, port = get_url_parts("localhost:3000")
    assert server == "localhost"
    assert port == 3000

    server, port = get_url_parts("localhost")
    assert server == "localhost"
    assert port is None

    server, port = get_url_parts("127.0.0.1")
    assert server == "127.0.0.1"
    assert port is None
