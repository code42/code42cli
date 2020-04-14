import code42cli.cmds.detectionlists.high_risk as high_risk
from code42cli.commands import Command


def load_subcommands():
    return [
        Command(
            u"high-risk",
            u"Add or remove users from the `high risk` detection list.",
            subcommand_loader=high_risk.load_subcommands,
        )
    ]
