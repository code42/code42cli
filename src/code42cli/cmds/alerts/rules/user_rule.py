from clients.alerts import get_all, get_by_name, _get_alert_rules


def load_subcommands():
    pass


def add(sdk, rule_id, identifier, aliases):
    return sdk.alerts.rules.add_rules(rule_id, identifier, aliases)


def remove(sdk, rule_id, identifier):
    return sdk.alerts.rules.remove_users(rule_id, identifier)
    

def remove_all(sdk, rule_id):
    return sdk.alerts.rules.remove_all_users(rule_id)


def get(sdk, rule_type, rule_id):
    return sdk.alerts.rules.get(rule_type, rule_id)


def get_all(sdk):
    return get_all(sdk.alerts.rules._user_context, _get_alert_rules)
    

def get_by_name(sdk, rule_name):
    return get_by_name(sdk.alerts.rules._user_context, _get_alert_rules, rule_name)
