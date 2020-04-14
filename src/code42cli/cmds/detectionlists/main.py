import code42cli.cmds.detectionlists.high_risk as high_risk
import code42cli.cmds.detectionlists.departing_employee as de
from code42cli.cmds.detectionlists.enums import DetectionLists
from code42cli.commands import Command


def load_subcommands():
    description = u"Add or remove users from the {} detection list."

    return [
        Command(
            DetectionLists.HIGH_RISK,
            description.format(DetectionLists.HIGH_RISK),
            subcommand_loader=high_risk.load_subcommands,
        ),
        
        Command(
            DetectionLists.DEPARTING_EMPLOYEE,
            description.format(DetectionLists.DEPARTING_EMPLOYEE),
            subcommand_loader=de.load_subcommands,
        )
    ]
