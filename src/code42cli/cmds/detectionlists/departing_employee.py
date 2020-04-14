from code42cli.commands import Command


def load_subcommands():
    bulk = Command(
        u"bulk",
        u"Tools for executing bulk departing employee commands.",
        subcommand_loader=load_bulk_subcommands,
    )
    add = Command(
        u"add",
        u"Add a user to the departing employee detection list.",
        u"{} add <username> <optional args>".format(_USAGE_PREFIX),
        handler=add_high_risk_employee,
        arg_customizer=_load_add_description,
    )
    return [bulk, add]
