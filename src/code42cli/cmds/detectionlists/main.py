import code42cli.cmds.detectionlists.departing_employee as de
from code42cli.commands import Command


def load_subcommands():
    return [
        Command(
            u"departingemployee",
            u"Add or remove users from the `departing employee` detection list.",
            subcommand_loader=de.load_subcommands,
        ),
    ]
