from code42cli.cmds.search.output_processor import print_events
from code42cli.cmds.search.output_processor import send_events
from code42cli.output_formats import to_table


EVENTS = [
    {"test": "value1", "test2": "value2"},
    {"test": "value", "test2": "value2"},
    {"test": "valuea", "test2": "value2"},
    {"test": "valueb", "test2": "value2"},
    {"test": "valuec", "test2": "value2"},
    {"test": "valued", "test2": "value2"},
    {"test": "valuee", "test2": "value2"},
    {"test": "valuef", "test2": "value2"},
    {"test": "valueg", "test2": "value2"},
    {"test": "valueh", "test2": "value2"},
]


def test_print_events_calls_echo_when_results_are_less_than_equal_to_10(mocker):
    mocked_echo = mocker.patch("click.echo")
    print_events(to_table, True, {"test": "Test"})(EVENTS)
    assert mocked_echo.assert_called_once() is None


def test_print_events_calls_echo_via_pager_when_results_are_greater_than_10(mocker):
    mocked_echo_pager = mocker.patch("click.echo_via_pager")
    EVENTS.append({"test": "valueX", "test2": "value2"})
    print_events(to_table, True, {"test": "Test"})(EVENTS)
    assert mocked_echo_pager.assert_called_once() is None
