import code42cli.cmds.detectionlists.departing_employee as de
import code42cli.cmds.detectionlists.high_risk as high_risk
from code42cli.commands import Command


def load_subcommands():
    return [
        Command(
            u"departingemployee",
            u"Add or remove users from the `departing employee` detection list.",
            subcommand_loader=de.load_subcommands,
        ),
        # Command(
        #     u"hishrisk",
        #     u"Add ore remove users from the `high risk` detection list.",
        #     subcommand_loader=high_risk.load_subcommands,
        # ),
    ]
