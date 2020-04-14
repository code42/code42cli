from code42cli.cmds.detectionlists.enums import BulkCommandType
from code42cli.bulk import generate_template, create_bulk_processor
from code42cli.commands import Command

_USAGE_PREFIX = u"code452 detection-lists high-risk"


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


def load_bulk_subcommands():
    _usage_prefix = u"{} bulk".format(_USAGE_PREFIX)

    generate_template_cmd = Command(
        u"generate-template",
        u"Generates the necessary csv template needed for bulk adding users.",
        u"{} gen-template <cmd> <optional args>".format(_usage_prefix),
        handler=generate_csv_file,
        arg_customizer=_load_bulk_generate_template_description,
    )
    add = Command(
        u"add",
        u"Bulk add users to the departing employee detection list using a csv file.",
        u"{} add <csv-file>".format(_usage_prefix),
        handler=bulk_add_high_risk_employees,
        arg_customizer=_load_bulk_add_description,
    )
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
