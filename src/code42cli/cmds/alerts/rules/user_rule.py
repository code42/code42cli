from collections import OrderedDict

from py42.exceptions import Py42InternalServerError
from py42.util import format_json


from code42cli.errors import InvalidRuleTypeError
from code42cli.util import format_to_table, find_format_width, get_user_id
from code42cli.bulk import run_bulk_process
from code42cli.file_readers import create_csv_reader
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.alerts.rules.enums import AlertRuleTypes


_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP[u"observerRuleId"] = u"RuleId"
_HEADER_KEYS_MAP[u"name"] = u"Name"
_HEADER_KEYS_MAP[u"severity"] = u"Severity"
_HEADER_KEYS_MAP[u"type"] = u"Type"
_HEADER_KEYS_MAP[u"ruleSource"] = u"Source"
_HEADER_KEYS_MAP[u"isEnabled"] = u"Enabled"


def add_user(sdk, profile, rule_id, username):
    user_id = get_user_id(sdk, username)
    rules = _get_rule_metadata(sdk, rule_id)
    try:
        if rules:
            sdk.alerts.rules.add_user(rule_id, user_id)
    except Py42InternalServerError as e:
        _check_if_system_rule(sdk, rules)
        raise


def remove_user(sdk, profile, rule_id, username):
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


def get_rules(sdk, profile):
    selected_rules = _get_all_rules_metadata(sdk)
    if selected_rules:
        rows, column_size = find_format_width(selected_rules, _HEADER_KEYS_MAP)
        format_to_table(rows, column_size)


def add_bulk_users(sdk, profile, file_name):
    reader = create_csv_reader(file_name)
    run_bulk_process(lambda rule_id, username: add_user(sdk, profile, rule_id, username), reader)


def remove_bulk_users(sdk, profile, file_name):
    reader = create_csv_reader(file_name)
    run_bulk_process(lambda rule_id, username: remove_user(sdk, profile, rule_id, username), reader)


def show_rule(sdk, profile, rule_id):
    selected_rule = _get_rule_metadata(sdk, rule_id)
    rule_detail = None
    if selected_rule:
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
