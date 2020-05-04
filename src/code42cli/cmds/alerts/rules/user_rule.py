def add_user(sdk, rule_id, user_id):
    response = sdk.alerts.rules.add_user(rule_id, user_id)
    print(response)


def remove_user(sdk, rule_id, user_id):
    response = sdk.alerts.rules.remove_user(rule_id, user_id)
    print(response)
    

def remove_all_users(sdk, rule_id):
    response = sdk.alerts.rules.remove_all_users(rule_id)
    print(response)


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
    

def get_by_name(sdk, rule_name):
    rules = sdk.alerts.rules.get_by_name(rule_name)
    print(rules)
