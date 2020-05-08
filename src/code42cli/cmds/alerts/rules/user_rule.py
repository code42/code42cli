from code42cli.bulk import run_bulk_process, CSVReader
from code42cli.cmds.detectionlists import get_user_id


def add_user(sdk, profile, rule_id, user_name):
    user_id = get_user_id(sdk, user_name)
    sdk.alerts.rules.add_user(rule_id, user_id)


def remove_user(sdk, profile, rule_id, user_name=None):
    if user_name:
        user_id = get_user_id(sdk, user_name)
        sdk.alerts.rules.remove_user(rule_id, user_id)
    else:
        sdk.alerts.rules.remove_all_users(rule_id)


def get_rules(sdk, profile, rule_id=None):
    rules_generator = sdk.alerts.rules.get_all()
    selected_rules = []
    if rule_id:
        selected_rules.append(
            rule for rules in rules_generator 
            for rule in rules["ruleMetadata"] 
            if rule["observerRuleId"] == rule_id
        )
    else:
        for rules in rules_generator:
            for rule in rules["ruleMetadata"]:
                selected_rules.append(rule)
    print(selected_rules)


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
