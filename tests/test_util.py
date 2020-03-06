from code42cli.util import get_url_parts


def test_get_url_parts_when_given_scheme_host_and_port_returns_expected_parts():
    url_str = "https://www.example.com:123"
    parts = get_url_parts(url_str)
    assert parts[0] == "www.example.com"
    assert parts[1] == 123


def test_get_url_parts_when_given_host_and_port_returns_expected_parts():
    url_str = "www.example.com:123"
    parts = get_url_parts(url_str)
    assert parts[0] == "www.example.com"
    assert parts[1] == 123


def test_get_url_parts_when_given_host_without_port_returns_expected_parts():
    url_str = "www.example.com"
    parts = get_url_parts(url_str)
    assert parts[0] == "www.example.com"
    assert parts[1] is None
