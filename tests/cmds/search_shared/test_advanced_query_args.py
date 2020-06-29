import pytest
from code42cli.cmds.search.extraction import exit_if_advanced_query_used_with_other_search_args
from code42cli.cmds.search.enums import FileEventFilterArguments, AlertFilterArguments


def test_exit_if_advanced_query_provided_incompatible_args(
    mocker, file_event_namespace, alert_namespace
):
    mock = mocker.patch(
        "code42cli.cmds.search.extraction.create_advanced_query_incompatible_search_args"
    )
    mock.return_value = {
        "invalid_arg": None,
    }
    file_event_namespace.invalid_arg = "value"
    with pytest.raises(SystemExit):
        exit_if_advanced_query_used_with_other_search_args(
            file_event_namespace, FileEventFilterArguments()
        )

    alert_namespace.invalid_arg = "value"
    with pytest.raises(SystemExit):
        exit_if_advanced_query_used_with_other_search_args(alert_namespace, AlertFilterArguments())
