import code42cli.cmds.detectionlists.high_risk as de
from code42cli.commands import Command


def load_subcommands():
    return [
        Command(
            u"high-risk",
            u"Add or remove users from the `departing employee` detection list.",
            subcommand_loader=de.load_subcommands,
        ),
    ]
