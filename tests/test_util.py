import pytest

from code42cli import PRODUCT_NAME
from code42cli.util import does_user_agree
from code42cli.util import find_format_width

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


_NAMESPACE = "{}.util".format(PRODUCT_NAME)


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
