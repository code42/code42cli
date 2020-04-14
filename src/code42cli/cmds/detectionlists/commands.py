from code42cli.commands import Command


def create_bulk_command(detection_list_type):
    """Creates a command for housing bulk subcommands.
    
    Args:
        detection_list_type (str): Either of the values from the enum DetectionLists ("high-risk" 
            or "departing-employee").
    """
    return Command(
        u"bulk",
        u"Tools for executing bulk {} commands.".format(detection_list_type),
        subcommand_loader=load_bulk_subcommands,
    )

