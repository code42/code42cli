from code42cli.bulk import generate_template, create_bulk_processor
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
        handler=add_high_risk_employee,
        arg_customizer=_load_add_description,
    )
    return [bulk, add]


def load_bulk_subcommands():
    gen_template = Command(
        u"gen-template",
        u"Generates the necessary csv template needed for bulk adding users.",
        handler=generate_csv_file,
    )
    add = Command(
        u"add",
        u"Bulk add users to the departing employee detection list using a csv file.",
        handler=bulk_add_high_risk_employees,
        arg_customizer=_load_bulk_add_description,
    )
    return [gen_template, add]


def generate_csv_file(path=None):
    """Generates a csv template a user would need to fill-in for bulk adding users to the high 
    risk detection list."""
    generate_template(add_high_risk_employee, path)


def bulk_add_high_risk_employees(sdk, profile, csv_file):
    """Takes a csv file in the form `user_id,risk_factors` with each row representing an 
    employee and adds each employee to the high risk detection list in a bulk fashion.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        csv_file (str): The path to the csv file containing rows of users.
    """
    processor = create_bulk_processor(
        csv_file, lambda **kwargs: add_high_risk_employee(sdk, profile, **kwargs)
    )
    processor.run()


def add_high_risk_employee(sdk, profile, user_id, risk_factors=None):
    """Adds the user with the given user profile ID to the high risk detection list.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        user_id (str): The ID for the user profile in detection lists.
        risk_factors (iter[str]): The list of risk factors associated with the user.
    """


def _load_add_description(argument_collection):
    user_id = argument_collection.arg_configs[u"user_id"]
    risk_factors = argument_collection.arg_configs[u"risk_factors"]
    user_id.set_help(u"A user profile ID for detection lists.")
    risk_factors.set_help(u"Risk factors associated with the employee.")


def _load_bulk_add_description(argument_collection):
    csv_file = argument_collection.arg_configs[u"csv_file"]
    csv_file.set_help(
        u"The path to the csv file for bulk adding users to the high risk detection list."
    )
