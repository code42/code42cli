import platform
import signal
import sys

from py42.settings import set_user_agent_suffix

from code42cli import PRODUCT_NAME
from code42cli.cmds.detectionlists import departing_employee as de
from code42cli.cmds.detectionlists import high_risk_employee as hre
from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.cmds.securitydata import main as secmain
from code42cli.cmds.alerts import main as alertmain
from code42cli.cmds.alerts.rules import commands as alertrules
from code42cli.cmds.profile import ProfileCommandController
from code42cli.commands import Command, CommandController
from code42cli.invoker import CommandInvoker


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    sys.exit(1)


signal.signal(signal.SIGINT, exit_on_interrupt)


# If on Windows, configure console session to handle ANSI escape sequences correctly
# source: https://bugs.python.org/issue29059
if platform.system().lower() == u"windows":
    from ctypes import windll, c_int, byref

    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)


# Sets part of the user agent string that py42 attaches to requests for the purposes of
# identifying CLI users.
set_user_agent_suffix(PRODUCT_NAME)


class MainCommandController(CommandController):
    PROFILE = u"profile"
    SECURITY_DATA = u"security-data"
    ALERTS = u"alerts"
    ALERT_RULES = u"alert-rules"
    DEPARTING_EMPLOYEE = DetectionLists.DEPARTING_EMPLOYEE
    HIGH_RISK_EMPLOYEE = DetectionLists.HIGH_RISK_EMPLOYEE

    @property
    def table(self):
        return {
            u"": self,
            self.PROFILE: self._create_profile_controller(),
            self.SECURITY_DATA: self._create_security_data_controller(),
            self.ALERTS: self._create_alerts_controller(),
            self.ALERT_RULES: self._create_alert_rules_controller(),
            self.DEPARTING_EMPLOYEE: self._create_departing_employee_controller(),
            self.HIGH_RISK_EMPLOYEE: self._create_high_risk_employee_controller(),
        }

    @property
    def names(self):
        return [
            self.PROFILE,
            self.SECURITY_DATA,
            self.ALERTS,
            self.ALERT_RULES,
            self.DEPARTING_EMPLOYEE,
            self.HIGH_RISK_EMPLOYEE,
        ]

    def load_commands(self):
        detection_lists_description = (
            u"For adding and removing employees from the {} detection list."
        )
        return [
            Command(
                self.PROFILE,
                u"For managing Code42 settings.",
                subcommand_loader=self.table[self.PROFILE].load_commands,
            ),
            Command(
                self.SECURITY_DATA,
                u"Tools for getting security related data, such as file events.",
                subcommand_loader=self.table[self.SECURITY_DATA].load_commands,
            ),
            Command(
                self.ALERTS,
                u"Tools for getting alert data.",
                subcommand_loader=self.table[self.ALERTS].load_commands,
            ),
            Command(
                self.ALERT_RULES,
                u"Manage alert rules.",
                subcommand_loader=self.table[self.ALERT_RULES].load_commands,
            ),
            Command(
                self.DEPARTING_EMPLOYEE,
                detection_lists_description.format(u"departing employee"),
                subcommand_loader=self.table[self.DEPARTING_EMPLOYEE].load_commands,
            ),
            Command(
                self.HIGH_RISK_EMPLOYEE,
                detection_lists_description.format(u"high risk employee"),
                subcommand_loader=self.table[self.HIGH_RISK_EMPLOYEE].load_commands,
            ),
        ]

    def _create_profile_controller(self):
        return ProfileCommandController(self.PROFILE)

    def _create_security_data_controller(self):
        return secmain.SecurityDataCommandController(self.SECURITY_DATA)

    def _create_alerts_controller(self):
        return alertmain.MainAlertsCommandController(self.ALERTS)

    def _create_alert_rules_controller(self):
        return alertrules.AlertRulesCommandController(self.ALERT_RULES)

    def _create_departing_employee_controller(self):
        return de.DepartingEmployeeCommandController(self.DEPARTING_EMPLOYEE)

    def _create_high_risk_employee_controller(self):
        return hre.HighRiskEmployeeCommandController(self.HIGH_RISK_EMPLOYEE)


def main():
    top = Command(u"", u"", subcommand_loader=MainCommandController(u"").load_commands)
    invoker = CommandInvoker(top)
    invoker.run(sys.argv[1:])


if __name__ == u"__main__":
    main()
