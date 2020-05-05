from code42cli.bulk import run_bulk_process, CSVTupleReader


def add_user(sdk, rule_id, user_id):
    sdk.alerts.rules.add_user(rule_id, user_id)
    

def remove_user(sdk, rule_id, user_id):
    sdk.alerts.rules.remove_user(rule_id, user_id)
    

def remove_all_users(sdk, rule_id):
    sdk.alerts.rules.remove_all_users(rule_id)
    

def _get_rule_category(sdk, rule_type):
    if rule_type == u"exfiltrator":
        return sdk.alerts.rules.exfiltrator
    elif rule_type == u"cloudshare":
        return sdk.alerts.rules.cloudshare
    elif rule_type == u"filetypemismatch":
        return sdk.alerts.rules.filetypemismatch
    else:
        return None


def get_by_rule_type(sdk, rule_type, rule_id):
    rule_category = _get_rule_category(sdk, rule_type)
    if rule_category:
        rule = rule_category.get(rule_id)
        print(rule)


def get_all(sdk):
    rules_gen = sdk.alerts.rules.get_all()
    for rule in rules_gen:
        print(rule)


def add_bulk_users(sdk, file_name):
    run_bulk_process(
        file_name, 
        lambda rule_id, user_id: sdk.alerts.rules.add_user(rule_id, user_id),
        CSVTupleReader()
    )


def _remove_users(sdk, rule_id, user_id):
    if user_id:
        remove_user(sdk, rule_id, user_id)
    else:
        remove_all_users(sdk, rule_id)


def remove_bulk_users(sdk, file_name):
    run_bulk_process(
        file_name,
        lambda rule_id, user_id: _remove_users(sdk, rule_id, user_id),
        CSVTupleReader()
    )
