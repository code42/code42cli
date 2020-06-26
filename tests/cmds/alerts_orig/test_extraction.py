import logging

import pytest
from click.testing import CliRunner
from py42.sdk.queries.alerts.filters import *

from code42cli.main import cli
from code42cli.cmds.alerts import _extract
import code42cli.errors as errors
from code42cli import PRODUCT_NAME
from c42eventextractor.extractors import AlertExtractor
from code42cli.errors import Code42CLIError
from tests.cmds.conftest import get_filter_value_from_json
from ...conftest import get_test_date_str, begin_date_str, ErrorTrackerTestHelper

from click.testing import CliRunner


@pytest.fixture
def alert_extractor(mocker):
    mock = mocker.patch("code42cli.cmds.alerts._get_alert_extractor")
    mock.return_value = mocker.MagicMock(spec=AlertExtractor)
    return mock


@pytest.fixture
def alert_namespace_with_begin(alert_namespace):
    alert_namespace.begin = begin_date_str
    return alert_namespace


@pytest.fixture
def alert_checkpoint(mocker):
    return mocker.patch(
        "{}.cmds.search_shared.cursor_store.AlertCursorStore.get_stored_cursor_timestamp".format(
            PRODUCT_NAME
        )
    )


def filter_term_is_in_call_args(extractor, term):
    arg_filters = extractor.extract.call_args[0]
    for f in arg_filters:
        if term in str(f):
            return True
    return False


def test_extract_when_is_advanced_query_uses_only_the_extract_advanced(cli_state, alert_extractor):
    runner = CliRunner()
    runner.invoke(cli, ["alerts", "print", "--advanced-query", "some complex json"], obj=cli_state)
    # alert_extractor.extract_advanced.assert_called_once_with("some complex json")
    assert alert_extractor.extract.call_count == 0


# def test_extract_when_is_advanced_query_and_has_begin_date_exits(
#     sdk, profile, logger, alert_namespace
# ):
#     alert_namespace.advanced_query = "some complex json"
#     alert_namespace.begin = "begin date"
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_is_advanced_query_and_has_end_date_exits(
#     sdk, profile, logger, alert_namespace
# ):
#     alert_namespace.advanced_query = "some complex json"
#     alert_namespace.end = "end date"
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# @pytest.mark.parametrize(
#     "arg",
#     [
#         "severity",
#         "actor",
#         "actor_contains",
#         "exclude_actor",
#         "exclude_actor_contains",
#         "rule_name",
#         "exclude_rule_name",
#         "rule_id",
#         "exclude_rule_id",
#         "rule_type",
#         "exclude_rule_type",
#     ],
# )
# def test_extract_when_is_advanced_query_and_other_incompatible_multi_narg_argument_passed(
#     sdk, profile, logger, alert_namespace, arg
# ):
#     alert_namespace.advanced_query = "some complex json"
#     setattr(alert_namespace, arg, ["test_value"])
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# @pytest.mark.parametrize("arg", ["state", "description"])
# def test_extract_when_is_advanced_query_and_other_incompatible_single_arg_argument_passed(
#     sdk, profile, logger, alert_namespace, arg
# ):
#     alert_namespace.advanced_query = "some complex json"
#     setattr(alert_namespace, arg, "test_value")
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_is_advanced_query_and_has_incremental_mode_exits(
#     sdk, profile, logger, file_event_namespace
# ):
#     file_event_namespace.advanced_query = "some complex json"
#     file_event_namespace.incremental = True
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, file_event_namespace)
#
#
# def test_extract_when_is_advanced_query_and_has_incremental_mode_set_to_false_does_not_exit(
#     sdk, profile, logger, alert_namespace
# ):
#     alert_namespace.advanced_query = "some complex json"
#     alert_namespace.is_incremental = False
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_is_not_advanced_query_uses_only_extract_method(
#     sdk, profile, logger, alert_extractor, alert_namespace_with_begin
# ):
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert alert_extractor.extract.call_count == 1
#     assert alert_extractor.extract_raw.call_count == 0
#
#
# def test_extract_when_not_given_begin_or_advanced_causes_exit(
#     sdk, profile, logger, alert_namespace
# ):
#     alert_namespace.begin = None
#     alert_namespace.advanced_query = None
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_given_begin_date_uses_expected_query(
#     sdk, profile, logger, alert_namespace, alert_extractor
# ):
#     alert_namespace.begin = get_test_date_str(days_ago=89)
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#     actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=0)
#     expected = "{0}T00:00:00.000Z".format(alert_namespace.begin)
#     assert actual == expected
#
#
# def test_extract_when_given_begin_date_and_time_uses_expected_query(
#     sdk, profile, logger, alert_namespace, alert_extractor
# ):
#     date = get_test_date_str(days_ago=89)
#     time = "15:33:02"
#     alert_namespace.begin = get_test_date_str(days_ago=89) + " " + time
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#     actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=0)
#     expected = "{0}T{1}.000Z".format(date, time)
#     assert actual == expected
#
#
# def test_extract_when_given_begin_date_and_time_without_seconds_uses_expected_query(
#     sdk, profile, logger, alert_namespace, alert_extractor
# ):
#     date = get_test_date_str(days_ago=89)
#     time = "15:33"
#     alert_namespace.begin = get_test_date_str(days_ago=89) + " " + time
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#     actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=0)
#     expected = "{0}T{1}:00.000Z".format(date, time)
#     assert actual == expected
#
#
# def test_extract_when_given_end_date_uses_expected_query(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.end = get_test_date_str(days_ago=10)
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=1)
#     expected = "{0}T23:59:59.999Z".format(alert_namespace_with_begin.end)
#     assert actual == expected
#
#
# def test_extract_when_given_end_date_and_time_uses_expected_query(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     date = get_test_date_str(days_ago=10)
#     time = "12:00:11"
#     alert_namespace_with_begin.end = date + " " + time
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=1)
#     expected = "{0}T{1}.000Z".format(date, time)
#     assert actual == expected
#
#
# def test_extract_when_given_end_date_and_time_without_seconds_uses_expected_query(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     date = get_test_date_str(days_ago=10)
#     time = "12:00"
#     alert_namespace_with_begin.end = date + " " + time
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     actual = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=1)
#     expected = "{0}T{1}:00.000Z".format(date, time)
#     assert actual == expected
#
#
# def test_extract_when_using_both_min_and_max_dates_uses_expected_timestamps(
#     sdk, profile, logger, alert_namespace, alert_extractor
# ):
#     end_date = get_test_date_str(days_ago=55)
#     end_time = "13:44:44"
#     alert_namespace.begin = get_test_date_str(days_ago=89)
#     alert_namespace.end = end_date + " " + end_time
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#     actual_begin_timestamp = get_filter_value_from_json(
#         alert_extractor.extract.call_args[0][0], filter_index=0
#     )
#     actual_end_timestamp = get_filter_value_from_json(
#         alert_extractor.extract.call_args[0][0], filter_index=1
#     )
#     expected_begin_timestamp = "{0}T00:00:00.000Z".format(alert_namespace.begin)
#     expected_end_timestamp = "{0}T{1}.000Z".format(end_date, end_time)
#
#     assert actual_begin_timestamp == expected_begin_timestamp
#     assert actual_end_timestamp == expected_end_timestamp
#
#
# def test_extract_when_given_min_timestamp_more_than_ninety_days_back_in_ad_hoc_mode_causes_exit(
#     sdk, profile, logger, alert_namespace
# ):
#     alert_namespace.incremental = False
#     date = get_test_date_str(days_ago=91) + " 12:51:00"
#     alert_namespace.begin = date
#     with pytest.raises(DateArgumentError):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_end_date_is_before_begin_date_causes_exit(
#     sdk, profile, logger, alert_namespace
# ):
#     alert_namespace.begin = get_test_date_str(days_ago=5)
#     alert_namespace.end = get_test_date_str(days_ago=6)
#     with pytest.raises(DateArgumentError):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_when_given_begin_date_past_90_days_and_is_incremental_and_a_stored_cursor_exists_and_not_given_end_date_does_not_use_any_event_timestamp_filter(
#     sdk, profile, logger, alert_namespace, alert_extractor, alert_checkpoint
# ):
#     alert_namespace.begin = "2019-01-01"
#     alert_namespace.incremental = True
#     alert_checkpoint.return_value = 22624624
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#     assert not filter_term_is_in_call_args(alert_extractor, DateObserved._term)
#
#
# def test_when_given_begin_date_and_not_interactive_mode_and_cursor_exists_uses_begin_date(
#     sdk, profile, logger, alert_namespace, alert_extractor, alert_checkpoint
# ):
#     alert_namespace.begin = get_test_date_str(days_ago=1)
#     alert_namespace.incremental = False
#     alert_checkpoint.return_value = 22624624
#     extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#     actual_ts = get_filter_value_from_json(alert_extractor.extract.call_args[0][0], filter_index=0)
#     expected_ts = "{0}T00:00:00.000Z".format(alert_namespace.begin)
#     assert actual_ts == expected_ts
#     assert filter_term_is_in_call_args(alert_extractor, DateObserved._term)
#
#
# def test_when_not_given_begin_date_and_is_incremental_but_no_stored_checkpoint_exists_causes_exit(
#     sdk, profile, logger, alert_namespace, alert_checkpoint
# ):
#     alert_namespace.begin = None
#     alert_namespace.is_incremental = True
#     alert_checkpoint.return_value = None
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_given_actor_is_uses_username_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.actor = ["test.testerson@example.com"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         Actor.is_in(alert_namespace_with_begin.actor)
#     )
#
#
# def test_extract_when_given_exclude_actor_uses_actor_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.exclude_actor = ["test.testerson"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         Actor.not_in(alert_namespace_with_begin.exclude_actor)
#     )
#
#
# def test_extract_when_given_rule_name_uses_rule_name_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.rule_name = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         RuleName.is_in(alert_namespace_with_begin.rule_name)
#     )
#
#
# def test_extract_when_given_exclude_rule_name_uses_rule_name_not_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.exclude_rule_name = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         RuleName.not_in(alert_namespace_with_begin.exclude_rule_name)
#     )
#
#
# def test_extract_when_given_rule_type_uses_rule_name_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.rule_type = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         RuleType.is_in(alert_namespace_with_begin.rule_type)
#     )
#
#
# def test_extract_when_given_exclude_rule_type_uses_rule_name_not_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.exclude_rule_type = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         RuleType.not_in(alert_namespace_with_begin.exclude_rule_type)
#     )
#
#
# def test_extract_when_given_rule_id_uses_rule_name_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.rule_id = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         RuleId.is_in(alert_namespace_with_begin.rule_id)
#     )
#
#
# def test_extract_when_given_exclude_rule_id_uses_rule_name_not_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.exclude_rule_id = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         RuleId.not_in(alert_namespace_with_begin.exclude_rule_id)
#     )
#
#
# def test_extract_when_given_description_uses_description_filter(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.description = ["catch the bad guys"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         Description.contains(alert_namespace_with_begin.description)
#     )
#
#
# def test_extract_when_given_multiple_search_args_uses_expected_filters(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor
# ):
#     alert_namespace_with_begin.actor = ["test.testerson@example.com"]
#     alert_namespace_with_begin.exclude_actor = ["flag.flagerson@code42.com"]
#     alert_namespace_with_begin.rule_name = ["departing employee"]
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     assert str(alert_extractor.extract.call_args[0][1]) == str(
#         Actor.is_in(alert_namespace_with_begin.actor)
#     )
#     assert str(alert_extractor.extract.call_args[0][2]) == str(
#         Actor.not_in(alert_namespace_with_begin.exclude_actor)
#     )
#     assert str(alert_extractor.extract.call_args[0][3]) == str(
#         RuleName.is_in(alert_namespace_with_begin.rule_name)
#     )
#
#
# def test_extract_when_creating_sdk_throws_causes_exit(
#     sdk, profile, logger, alert_namespace, mock_42
# ):
#     def side_effect():
#         raise Exception()
#
#     mock_42.side_effect = side_effect
#     with pytest.raises(SystemExit):
#         extraction_module.extract(sdk, profile, logger, alert_namespace)
#
#
# def test_extract_when_not_errored_and_does_not_log_error_occurred(
#     sdk, profile, logger, alert_namespace_with_begin, alert_extractor, caplog
# ):
#     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#     with caplog.at_level(logging.ERROR):
#         assert "View exceptions that occurred at" not in caplog.text
#
#
# # def test_extract_when_not_errored_and_is_interactive_does_not_print_error(
# #     sdk, profile, logger, alert_namespace_with_begin, alert_extractor, cli_logger, mocker
# # ):
# #     errors.ERRORED = False
# #     mocker.patch("code42cli.cmds.securitydata_mod.extraction.logger", cli_logger)
# #     extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
# #     assert cli_logger.print_and_log_error.call_count == 0
# #     assert cli_logger.log_error.call_count == 0
# #     errors.ERRORED = False
#
#
# def test_when_sdk_raises_exception_global_variable_gets_set(
#     mocker, sdk, profile, logger, alert_namespace_with_begin, mock_42
# ):
#     errors.ERRORED = False
#     mock_sdk = mocker.MagicMock()
#
#     def sdk_side_effect(self, *args):
#         raise Exception()
#
#     mock_sdk.security.search_file_events.side_effect = sdk_side_effect
#     mock_42.return_value = mock_sdk
#
#     mocker.patch("c42eventextractor.extractors.BaseExtractor._verify_filter_groups")
#     with ErrorTrackerTestHelper():
#         extraction_module.extract(sdk, profile, logger, alert_namespace_with_begin)
#         assert errors.ERRORED
