from collections import OrderedDict
import os

import click

from py42.exceptions import Py42InternalServerError
from py42.util import format_json


from code42cli.errors import InvalidRuleTypeError
from code42cli.util import format_to_table, find_format_width, get_user_id
from code42cli.bulk import run_bulk_process
from code42cli.file_readers import read_csv
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.alerts_mod.rules.enums import AlertRuleTypes
from code42cli.options import global_options
from code42cli.bulk import write_template_file

_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP[u"observerRuleId"] = u"RuleId"
_HEADER_KEYS_MAP[u"name"] = u"Name"
_HEADER_KEYS_MAP[u"severity"] = u"Severity"
_HEADER_KEYS_MAP[u"type"] = u"Type"
_HEADER_KEYS_MAP[u"ruleSource"] = u"Source"
_HEADER_KEYS_MAP[u"isEnabled"] = u"Enabled"


@click.group()
@global_options
def alert_rules(state):
    pass


rule_id_option = click.option("--rule-id", required=True, help="Observer ID of the rule.")
username_option = click.option("-u", "--username", required=True)


@alert_rules.command()
@rule_id_option
@click.option(
    "-u", "--username", required=True, help="The username of the user to add to the alert rule.",
)
@global_options
def add_user(state, rule_id, username):
    """Add a user to an alert rule."""
    _add_user(state.sdk, rule_id, username)


@alert_rules.command()
@rule_id_option
@click.option(
    "-u",
    "--username",
    required=True,
    help="The username of the user to remove from the alert rule.",
)
@global_options
def remove_user(state, rule_id, username):
    """Remove a user from an alert rule."""
    _remove_user(state.sdk, rule_id, username)


@alert_rules.command()
@global_options
def list(state):
    """Fetch existing alert rules."""
    selected_rules = _get_all_rules_metadata(state.sdk)
    if selected_rules:
        rows, column_size = find_format_width(selected_rules, _HEADER_KEYS_MAP)
        format_to_table(rows, column_size)


@alert_rules.command()
@click.argument("rule_id")
@global_options
def show(state, rule_id):
    """Print out detailed alert rule criteria."""
    selected_rule = _get_rule_metadata(state.sdk, rule_id)
    rule_detail = None
    if selected_rule:
        rule_type = selected_rule[0][u"type"]
        if rule_type == AlertRuleTypes.EXFILTRATION:
            rule_detail = state.sdk.alerts.rules.exfiltration.get(rule_id)
        elif rule_type == AlertRuleTypes.CLOUD_SHARE:
            rule_detail = state.sdk.alerts.rules.cloudshare.get(rule_id)
        elif rule_type == AlertRuleTypes.FILE_TYPE_MISMATCH:
            rule_detail = state.sdk.alerts.rules.filetypemismatch.get(rule_id)
    if rule_detail:
        logger = get_main_cli_logger()
        logger.print_info(format_json(rule_detail.text))


@alert_rules.group()
@global_options
def bulk(state):
    """Tools for executing bulk commands."""
    pass


@bulk.command()
@click.argument("cmd", type=click.Choice(["add", "remove"]))
@click.argument(
    "path", required=False, type=click.Path(dir_okay=False, resolve_path=True, writable=True)
)
def generate_template(cmd, path):
    """Generate the necessary csv template needed for bulk adding/removing users."""
    if not path:
        filename = "alert_rules_bulk_{}_users.csv".format(cmd)
        path = os.path.join(os.getcwd(), filename)
    write_template_file(path, columns=["rule_id", "username"])


path_arg = click.argument("path", type=click.File(mode="r"))


@bulk.command()
@path_arg
@global_options
def add_bulk_users(state, path):
    rows = read_csv(path)
    row_handler = lambda rule_id, username: _add_user(state.sdk, rule_id, username)
    run_bulk_process(row_handler, rows)


@bulk.command()
@path_arg
@global_options
def remove_bulk_users(state, path):
    rows = read_csv(path)
    row_handler = lambda rule_id, username: _remove_user(state.sdk, rule_id, username)
    run_bulk_process(row_handler, rows)


def _add_user(sdk, rule_id, username):
    user_id = get_user_id(sdk, username)
    rules = _get_rule_metadata(sdk, rule_id)
    try:
        if rules:
            sdk.alerts.rules.add_user(rule_id, user_id)
    except Py42InternalServerError as e:
        _check_if_system_rule(sdk, rules)
        raise


def _remove_user(sdk, rule_id, username):
    user_id = get_user_id(sdk, username)
    rules = _get_rule_metadata(sdk, rule_id)
    try:
        if rules:
            sdk.alerts.rules.remove_user(rule_id, user_id)
    except Py42InternalServerError as e:
        _check_if_system_rule(sdk, rules)
        raise


def _get_all_rules_metadata(sdk):
    rules_generator = sdk.alerts.rules.get_all()
    selected_rules = [rule for rules in rules_generator for rule in rules[u"ruleMetadata"]]
    return _handle_rules_results(sdk, selected_rules)


def _get_rule_metadata(sdk, rule_id):
    rules = sdk.alerts.rules.get_by_observer_id(rule_id)[u"ruleMetadata"]
    return _handle_rules_results(sdk, rules, rule_id)


def _handle_rules_results(sdk, rules, rule_id=None):
    id_msg = u"with RuleId {} ".format(rule_id) if rule_id else u""
    msg = u"No alert rules {0}found.".format(id_msg)
    if not rules:
        get_main_cli_logger().print_and_log_info(msg)
    return rules


def _check_if_system_rule(sdk, rules):
    if rules and rules[0][u"isSystem"]:
        raise InvalidRuleTypeError(rules[0][u"observerRuleId"], rules[0][u"ruleSource"])
