from code42cli.bulk import run_bulk_process, FlatFileReader


def add_user(sdk, rule_id, user_id):
    sdk.alerts.rules.add_user(rule_id, user_id)
    

def remove_user(sdk, rule_id, user_id=None):
    if user_id:
        sdk.alerts.rules.remove_user(rule_id, user_id)
    else:
        _remove_all_users(sdk, rule_id)


def _remove_all_users(sdk, rule_id):
    sdk.alerts.rules.remove_all_users(rule_id)
    

def _get_rule_category(sdk, rule_type):
    if rule_type == u"exfiltration":
        return sdk.alerts.rules.exfiltration
    elif rule_type == u"cloudshare":
        return sdk.alerts.rules.cloudshare
    elif rule_type == u"filetypemismatch":
        return sdk.alerts.rules.filetypemismatch
    else:
        return None


def _get_by_rule_type(sdk, rule_type, rule_id):
    rule_category = _get_rule_category(sdk, rule_type)
    if rule_category:
        rule = rule_category.get(rule_id)
        print(rule)


def _get_all(sdk):
    rules_gen = sdk.alerts.rules.get_all()
    for rule in rules_gen:
        print(rule)


def get_rules(sdk, rule_type=None, rule_id=None):
    if not rule_type and not rule_id:
        _get_all(sdk)
    else:
        _get_by_rule_type(sdk, rule_type, rule_id)


def _add_bulk_users(sdk, file_name):
    run_bulk_process(
        file_name, 
        lambda rule_id, user_id: sdk.alerts.rules.add_user(rule_id, user_id),
        FlatFileReader()
    )


def _remove_bulk_users(sdk, file_name):
    run_bulk_process(
        file_name,
        lambda rule_id, user_id: remove_user(sdk, rule_id, user_id),
        FlatFileReader()
    )


def bulk_update(sdk, action, file_name):
    if action == "add":
        _add_bulk_users(sdk, file_name)
    if action == 'remove':
        _remove_bulk_users(sdk, file_name)
