from code42cli.util import format_to_table, process_rules_for_formatting
from code42cli.bulk import run_bulk_process, CSVReader
from code42cli.cmds.detectionlists import get_user_id
from py42.util import format_json


HEADER_KEYS_MAP = {
    u"observerRuleId": u"RuleId", 
    u"name": u"Name", 
    u"severity": u"Severity", 
    u"type": u"Type", 
    u"ruleSource": u"Source",
    u"isEnabled": u"Enabled",
}



def add_user(sdk, profile, rule_id, user_name):
    user_id = get_user_id(sdk, user_name)
    sdk.alerts.rules.add_user(rule_id, user_id)


def remove_user(sdk, profile, rule_id, user_name=None):
    if user_name:
        user_id = get_user_id(sdk, user_name)
        sdk.alerts.rules.remove_user(rule_id, user_id)
    else:
        sdk.alerts.rules.remove_all_users(rule_id)


def _get_rules_metadata(sdk, rule_id):
    rules_generator = sdk.alerts.rules.get_all()
    selected_rules = []
    if rule_id:
        for rules in rules_generator:
            for rule in rules[u"ruleMetadata"]:
                if rule[u"observerRuleId"] == rule_id:
                    selected_rules.append(rule)
    else:
        for rules in rules_generator:
            for rule in rules[u"ruleMetadata"]:
                selected_rules.append(rule)
    return selected_rules


def get_rules(sdk, profile, rule_id=None):
    selected_rules = _get_rules_metadata(sdk, rule_id)
    rows, column_size = process_rules_for_formatting(selected_rules, HEADER_KEYS_MAP)
    format_to_table(rows, column_size)


def add_bulk_users(sdk, profile, file_name):
    run_bulk_process(
        file_name, 
        lambda rule_id, user_name: add_user(sdk, profile, rule_id, user_name),
        CSVReader()
    )


def remove_bulk_users(sdk, profile, file_name):
    run_bulk_process(
        file_name,
        lambda rule_id, user_name: remove_user(sdk, profile, rule_id, user_name),
        CSVReader()
    )


def show_rules(sdk, profile, rule_id):
    selected_rule = _get_rules_metadata(sdk, rule_id)
    rule_detail = None
    if len(selected_rule):
        rule_type = selected_rule[0][u"type"]
        if rule_type == 'FED_ENDPOINT_EXFILTRATION':
            rule_detail = sdk.alerts.rules.exfiltration.get(rule_id)
        elif rule_type == 'FED_CLOUD_SHARE_PERMISSIONS':
            rule_detail = sdk.alerts.rules.cloudshare.get(rule_id)
        elif rule_type == 'FED_FILE_TYPE_MISMATCH':
            rule_detail = sdk.alerts.rules.filetypemismatch.get(rule_id)
    if rule_detail:
        print(format_json(rule_detail.text))
