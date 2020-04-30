from code42cli.commands import Command
from code42cli.cmds.alerts.rules import user_rule

"""
Intended usages: 
ADD
code42 alert-rule add-user rule-id uid

code42 alert-rule remove-user rule-id
code42 alert-rule remove-user rule-id --uid value

code42 alert-rule get
code42 alert-rule get --name value
code42 alert-rule get rule-id --rule-type value 

"""


class AlertRulesCommandFactory(object):
    
    def __init__(self):
        self._name = u""
        
    def create_add_users_command(self):
        return Command(
            u"add-user",
            u"",
            handler= user_rule.add
            
        )   
    
    def create_remove_users_command(self):
        return Command(
            u"remove-users",
            u"",
            handler=user_rule.remove
            
        )
    
    def create_remove_all_users_command(self):
        return Command(
            u"remove-all-users",
            u"",
            handler=user_rule.remove_all
        )
    
    def create_get_command(self):
        return Command(
            u"get",
            u"",
            handler=user_rule.get
            
        )
    
    def create_get_all_command(self):
        return Command(
            u"get-all",
            u"",
            handler=user_rule.get_all
        )
    
    def create_get_by_name_command(self):
        return Command(
            u"get-by-name",
            u"",
            handler=user_rule.get_by_name
        )
