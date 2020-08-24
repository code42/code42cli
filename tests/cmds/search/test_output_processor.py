from _collections import OrderedDict

from code42cli.cmds.search.output_processor import print_events


header = OrderedDict()
header["test"] = "Test"
header["test2"] = "test2"

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

CSV_RESPONSE = "\r\n".join(
    [
        "test,test2",
        "value1,value2",
        "value,value2",
        "valuea,value2",
        "valueb,value2",
        "valuec,value2",
        "valued,value2",
        "valuee,value2",
        "valuef,value2",
        "valueg,value2",
        "valueh,value2",
        "",
    ]
)


def test_print_events_calls_echo_when_results_are_less_than_equal_to_10(mocker):
    format_function = mocker.MagicMock()
    format_function.return_value = CSV_RESPONSE
    mocked_echo = mocker.patch("click.echo")
    print_events(format_function, header)(EVENTS)
    mocked_echo.assert_called_once_with(CSV_RESPONSE)


def test_print_events_calls_echo_via_pager_when_results_are_greater_than_10(mocker):
    format_function = mocker.MagicMock()
    format_function.return_value = CSV_RESPONSE
    mocked_echo_pager = mocker.patch("click.echo_via_pager")
    EVENTS.append({"test": "valueX", "test2": "value2"})
    print_events(format_function, header)(EVENTS)
    assert mocked_echo_pager.call_count == 1
