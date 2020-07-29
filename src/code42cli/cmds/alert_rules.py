from collections import OrderedDict

import click
from click import echo
from py42.exceptions import Py42InternalServerError
from py42.util import format_json

from code42cli import PRODUCT_NAME
from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.cmds.shared import get_user_id
from code42cli.errors import Code42CLIError
from code42cli.errors import InvalidRuleTypeError
from code42cli.file_readers import read_csv_arg
from code42cli.options import OrderedGroup
from code42cli.options import sdk_options
from code42cli.output_formats import output_option
from code42cli.util import find_format_width
from code42cli.util import format_to_table


class AlertRuleTypes:
    EXFILTRATION = "FED_ENDPOINT_EXFILTRATION"
    CLOUD_SHARE = "FED_CLOUD_SHARE_PERMISSIONS"
    FILE_TYPE_MISMATCH = "FED_FILE_TYPE_MISMATCH"


_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP["observerRuleId"] = "RuleId"
_HEADER_KEYS_MAP["name"] = "Name"
_HEADER_KEYS_MAP["severity"] = "Severity"
_HEADER_KEYS_MAP["type"] = "Type"
_HEADER_KEYS_MAP["ruleSource"] = "Source"
_HEADER_KEYS_MAP["isEnabled"] = "Enabled"


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def alert_rules(state):
    """Manage alert rules."""
    pass


rule_id_option = click.option(
    "--rule-id", required=True, help="Observer ID of the rule."
)
username_option = click.option("-u", "--username", required=True)


@alert_rules.command()
@rule_id_option
@click.option(
    "-u",
    "--username",
    required=True,
    help="The username of the user to add to the alert rule.",
)
@sdk_options()
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
@sdk_options()
def remove_user(state, rule_id, username):
    """Remove a user from an alert rule."""
    _remove_user(state.sdk, rule_id, username)


@alert_rules.command("list")
@output_option
@sdk_options()
def list_alert_rules(state, format=None):
    """Fetch existing alert rules."""
    selected_rules = _get_all_rules_metadata(state.sdk)
    if selected_rules:
        if format:
            formatted_output = format(selected_rules, _HEADER_KEYS_MAP)
            echo(formatted_output)
        else:
            rows, column_size = find_format_width(selected_rules, _HEADER_KEYS_MAP)
            format_to_table(rows, column_size)


@alert_rules.command()
@click.argument("rule_id")
@sdk_options()
def show(state, rule_id):
    """Print out detailed alert rule criteria."""
    selected_rule = _get_rule_metadata(state.sdk, rule_id)
    if selected_rule:
        get = _get_rule_type_func(state.sdk, selected_rule[0]["type"])
        rule_detail = get(rule_id)
        echo(format_json(rule_detail.text))


@alert_rules.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk alert rule actions."""
    pass


ALERT_RULES_CSV_HEADERS = ["rule_id", "username"]

alert_rules_generate_template = generate_template_cmd_factory(
    group_name="alert_rules",
    commands_dict={"add": ALERT_RULES_CSV_HEADERS, "remove": ALERT_RULES_CSV_HEADERS},
)
bulk.add_command(alert_rules_generate_template)


@bulk.command(
    help="Bulk add users to alert rules from a csv file. CSV file format: {}".format(
        ",".join(ALERT_RULES_CSV_HEADERS)
    )
)
@read_csv_arg(headers=ALERT_RULES_CSV_HEADERS)
@sdk_options()
def add(state, csv_rows):
    sdk = state.sdk

    def handle_row(rule_id, username):
        _add_user(sdk, rule_id, username)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Adding users to alert-rules:"
    )


@bulk.command(
    help="Bulk remove users from alert rules from a csv file. CSV file format: {}".format(
        ",".join(ALERT_RULES_CSV_HEADERS)
    )
)
@read_csv_arg(headers=ALERT_RULES_CSV_HEADERS)
@sdk_options()
def remove(state, csv_rows):
    sdk = state.sdk

    def handle_row(rule_id, username):
        _remove_user(sdk, rule_id, username)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Removing users from alert-rules:"
    )


def _add_user(sdk, rule_id, username):
    user_id = get_user_id(sdk, username)
    rules = _get_rule_metadata(sdk, rule_id)
    try:
        if rules:
            sdk.alerts.rules.add_user(rule_id, user_id)
    except Py42InternalServerError:
        _check_if_system_rule(rules)
        raise


def _remove_user(sdk, rule_id, username):
    user_id = get_user_id(sdk, username)
    rules = _get_rule_metadata(sdk, rule_id)
    try:
        if rules:
            sdk.alerts.rules.remove_user(rule_id, user_id)
    except Py42InternalServerError:
        _check_if_system_rule(rules)
        raise


def _get_all_rules_metadata(sdk):
    rules_generator = sdk.alerts.rules.get_all()
    selected_rules = [
        rule for rules in rules_generator for rule in rules["ruleMetadata"]
    ]
    return _handle_rules_results(selected_rules)


def _get_rule_metadata(sdk, rule_id):
    rules = sdk.alerts.rules.get_by_observer_id(rule_id)["ruleMetadata"]
    return _handle_rules_results(rules, rule_id)


def _handle_rules_results(rules, rule_id=None):
    id_msg = "with RuleId {} ".format(rule_id) if rule_id else ""
    msg = "No alert rules {}found.".format(id_msg)
    if not rules:
        echo(msg)
    return rules


def _check_if_system_rule(rules):
    if rules and rules[0]["isSystem"]:
        raise InvalidRuleTypeError(rules[0]["observerRuleId"], rules[0]["ruleSource"])


def _get_rule_type_func(sdk, rule_type):
    if rule_type == AlertRuleTypes.EXFILTRATION:
        return sdk.alerts.rules.exfiltration.get
    elif rule_type == AlertRuleTypes.CLOUD_SHARE:
        return sdk.alerts.rules.cloudshare.get
    elif rule_type == AlertRuleTypes.FILE_TYPE_MISMATCH:
        return sdk.alerts.rules.filetypemismatch.get
    else:
        raise Code42CLIError(
            "Received an unknown rule type from server. You might need to update "
            "to a newer version of {}".format(PRODUCT_NAME)
        )
