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
from code42cli.cmds.legal_hold import commands as legalhold
from code42cli.cmds.profile import ProfileSubcommandLoader
from code42cli.commands import Command, SubcommandLoader
from code42cli.invoker import CommandInvoker
from code42cli.util import flush_stds_out_err_without_printing_error


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    print()
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


class MainSubcommandLoader(SubcommandLoader):
    PROFILE = u"profile"
    SECURITY_DATA = u"security-data"
    ALERTS = u"alerts"
    ALERT_RULES = u"alert-rules"
    DEPARTING_EMPLOYEE = DetectionLists.DEPARTING_EMPLOYEE
    HIGH_RISK_EMPLOYEE = DetectionLists.HIGH_RISK_EMPLOYEE
    LEGAL_HOLD = u"legal-hold"

    def load_commands(self):
        detection_lists_description = (
            u"For adding and removing employees from the {} detection list."
        )
        return [
            Command(
                self.PROFILE,
                u"For managing Code42 settings.",
                subcommand_loader=self._create_profile_loader(),
            ),
            Command(
                self.SECURITY_DATA,
                u"Tools for getting security related data, such as file events.",
                subcommand_loader=self._create_security_data_loader(),
            ),
            Command(
                self.ALERTS,
                u"Tools for getting alert data.",
                subcommand_loader=self._create_alerts_loader(),
            ),
            Command(
                self.ALERT_RULES,
                u"Manage alert rules.",
                subcommand_loader=self._create_alert_rules_loader(),
            ),
            Command(
                self.DEPARTING_EMPLOYEE,
                detection_lists_description.format(u"departing employee"),
                subcommand_loader=self._create_departing_employee_loader(),
            ),
            Command(
                self.HIGH_RISK_EMPLOYEE,
                detection_lists_description.format(u"high risk employee"),
                subcommand_loader=self._create_high_risk_employee_loader(),
            ),
            Command(
                self.LEGAL_HOLD,
                u"For adding and removing employees to legal hold matters.",
                subcommand_loader=self._create_legal_hold_loader(),
            ),
        ]

    def _create_profile_loader(self):
        return ProfileSubcommandLoader(self.PROFILE)

    def _create_security_data_loader(self):
        return secmain.SecurityDataSubcommandLoader(self.SECURITY_DATA)

    def _create_alerts_loader(self):
        return alertmain.MainAlertsSubcommandLoader(self.ALERTS)

    def _create_alert_rules_loader(self):
        return alertrules.AlertRulesSubcommandLoader(self.ALERT_RULES)

    def _create_departing_employee_loader(self):
        return de.DepartingEmployeeSubcommandLoader(self.DEPARTING_EMPLOYEE)

    def _create_high_risk_employee_loader(self):
        return hre.HighRiskEmployeeSubcommandLoader(self.HIGH_RISK_EMPLOYEE)

    def _create_legal_hold_loader(self):
        return legalhold.LegalHoldSubcommandLoader(self.LEGAL_HOLD)


def main():
    top = Command(u"", u"", subcommand_loader=MainSubcommandLoader(u""))
    invoker = CommandInvoker(top)
    try:
        invoker.run(sys.argv[1:])
    finally:
        flush_stds_out_err_without_printing_error()


if __name__ == u"__main__":
    main()
