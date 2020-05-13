from py42.util import format_json

from code42cli.util import format_to_table, find_format_width
from code42cli.bulk import run_bulk_process, CSVReader
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.detectionlists import get_user_id
from code42cli.cmds.alerts.rules.enums import AlertRuleTypes


_HEADER_KEYS_MAP = {
    u"observerRuleId": u"RuleId",
    u"name": u"Name",
    u"severity": u"Severity",
    u"type": u"Type",
    u"ruleSource": u"Source",
    u"isEnabled": u"Enabled",
}


def add_user(sdk, profile, rule_id=None, username=None):
    user_id = get_user_id(sdk, username)
    sdk.alerts.rules.add_user(rule_id, user_id)


def remove_user(sdk, profile, rule_id, username=None):
    if username:
        user_id = get_user_id(sdk, username)
        sdk.alerts.rules.remove_user(rule_id, user_id)
    else:
        sdk.alerts.rules.remove_all_users(rule_id)


def _get_rules_metadata(sdk, rule_id=None):
    rules_generator = sdk.alerts.rules.get_all()
    selected_rules = [rule for rules in rules_generator for rule in rules[u"ruleMetadata"]]
    if rule_id:
        selected_rules = [rule for rule in selected_rules if rule[u"observerRuleId"] == rule_id]
    return selected_rules


def get_rules(sdk, profile):
    selected_rules = _get_rules_metadata(sdk)
    rows, column_size = find_format_width(selected_rules, _HEADER_KEYS_MAP)
    format_to_table(rows, column_size)


def add_bulk_users(sdk, profile, file_name):
    run_bulk_process(
        file_name, lambda rule_id, username: add_user(sdk, profile, rule_id, username), CSVReader()
    )


def remove_bulk_users(sdk, profile, file_name):
    run_bulk_process(
        file_name,
        lambda rule_id, username: remove_user(sdk, profile, rule_id, username),
        CSVReader(),
    )


def show_rules(sdk, profile, rule_id):
    selected_rule = _get_rules_metadata(sdk, rule_id)
    rule_detail = None
    if len(selected_rule):
        rule_type = selected_rule[0][u"type"]
        if rule_type == AlertRuleTypes.EXFILTRATION:
            rule_detail = sdk.alerts.rules.exfiltration.get(rule_id)
        elif rule_type == AlertRuleTypes.CLOUD_SHARE:
            rule_detail = sdk.alerts.rules.cloudshare.get(rule_id)
        elif rule_type == AlertRuleTypes.FILE_TYPE_MISMATCH:
            rule_detail = sdk.alerts.rules.filetypemismatch.get(rule_id)
    if rule_detail:
        logger = get_main_cli_logger()
        logger.print_info(format_json(rule_detail.text))
