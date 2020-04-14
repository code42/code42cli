from code42cli.cmds.detectionlists.enums import BulkCommandType
from code42cli.cmds.detectionlists.commands import DetectionListCommandFactory, create_usage_prefix
from code42cli.bulk import generate_template, create_bulk_processor


_NAME = u"high-risk"
_USAGE_PREFIX = create_usage_prefix(_NAME)


def load_subcommands():
    factory = DetectionListCommandFactory(u"high-risk")
    bulk = factory.create_bulk_command(lambda: load_bulk_subcommands(factory))
    add = factory.create_add_command(add_high_risk_employee, _load_add_description)
    return [bulk, add]


def load_bulk_subcommands(factory):
    generate_template_cmd = factory.create_bulk_generate_template_command(
        generate_csv_file, _load_bulk_generate_template_description
    )

    add = factory.create_bulk_add_command(bulk_add_high_risk_employees, _load_bulk_add_description)
    return [generate_template_cmd, add]


def generate_csv_file(cmd, path=None):
    """Generates a csv template a user would need to fill-in for bulk adding users to the high 
    risk detection list."""
    handler = None
    if cmd == BulkCommandType.ADD:
        handler = add_high_risk_employee
    generate_template(handler, path)


def bulk_add_high_risk_employees(sdk, profile, csv_file):
    """Takes a csv file in the form `username,cloud_aliases,risk_factors,notes` with each row 
    representing an employee and adds each employee to the high risk detection list in a bulk 
    fashion.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        csv_file (str): The path to the csv file containing rows of users.
    """
    processor = create_bulk_processor(
        csv_file, lambda **kwargs: add_high_risk_employee(sdk, profile, **kwargs)
    )
    processor.run()


def add_high_risk_employee(
    sdk, profile, username, cloud_aliases=None, risk_factors=None, notes=None
):
    """Adds the user with the given username to the high risk detection list.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        username (str): The username for the user.
        cloud_aliases (iter[str]): A list of cloud aliases associated with the user.
        risk_factors (iter[str]): The list of risk factors associated with the user.
        notes (str): Notes about the user.
    """


def _load_add_description(argument_collection):
    username = argument_collection.arg_configs[u"username"]
    risk_factors = argument_collection.arg_configs[u"risk_factors"]
    username.set_help(u"A user profile ID for detection lists.")
    risk_factors.set_help(u"Risk factors associated with the employee.")


def _load_bulk_generate_template_description(argument_collection):
    cmd_type = argument_collection.arg_configs[u"cmd"]
    cmd_type.set_help(u"The type of command the template with be used for.")
    cmd_type.set_choices(BulkCommandType())


def _load_bulk_add_description(argument_collection):
    csv_file = argument_collection.arg_configs[u"csv_file"]
    csv_file.set_help(
        u"The path to the csv file for bulk adding users to the high risk detection list."
    )
