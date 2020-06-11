import pytest
from code42cli.parser import (
    exit_if_advanced_query_used_with_other_search_args,
)
from code42cli.cmds.search_shared.args import create_advanced_query_incompatible_search_args


def test_exit_if_advanced_query_provided_incompatible_args(
    file_event_namespace, alert_namespace
):
    file_event_namespace.advanced_query = "Not None"
    file_event_namespace.begin = "value"
    with pytest.raises(SystemExit):
        exit_if_advanced_query_used_with_other_search_args(
            file_event_namespace,
            list(create_advanced_query_incompatible_search_args().keys())
        )

    alert_namespace.advanced_query = "Not None"
    alert_namespace.begin = "value"
    with pytest.raises(SystemExit):
        exit_if_advanced_query_used_with_other_search_args(
            alert_namespace,
            list(create_advanced_query_incompatible_search_args().keys())
        )
