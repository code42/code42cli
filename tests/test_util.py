import pytest

from code42cli import PRODUCT_NAME
from code42cli.util import does_user_agree, get_url_parts


_NAMESPACE = "{}.util".format(PRODUCT_NAME)


@pytest.fixture
def mock_input(mocker):
    return mocker.patch("{}.get_input".format(_NAMESPACE))


def test_get_url_parts_when_given_host_and_port_returns_expected_parts():
    url_str = "www.example.com:123"
    parts = get_url_parts(url_str)
    assert parts == ("www.example.com", 123)


def test_get_url_parts_when_given_host_without_port_returns_expected_parts():
    url_str = "www.example.com"
    parts = get_url_parts(url_str)
    assert parts == ("www.example.com", None)


def test_does_user_agree_when_user_says_y_returns_true(mock_input):
    mock_input.return_value = "y"
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_capital_y_returns_true(mock_input):
    mock_input.return_value = "Y"
    assert does_user_agree("Test Prompt")


def test_does_user_agree_when_user_says_n_returns_false(mock_input):
    mock_input.return_value = "n"
    assert not does_user_agree("Test Prompt")
