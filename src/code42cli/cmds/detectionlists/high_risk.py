from code42cli.bulk import generate_template, BulkProcessor
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
    )
    return [bulk, add]


def load_bulk_subcommands():
    gen_template = Command(
        u"gen-template",
        u"Generates the necessary csv template needed for bulk adding users.",
        handler=create_csv_file,
    )
    add = Command(
        u"add",
        u"Bulk add users to the departing employee detection list using a .csv file.",
        handler=bulk_add_high_risk_employees
    )
    return [gen_template, add]

def create_csv_file(path=None):
    generate_template(add_high_risk_employee, path)


def add_high_risk_employee(sdk, profile, user_id, departure_date=None):
    # sdk.detectionlists.departing_employee.create(user_id, departure_date=departure_date)
    pass


def bulk_add_high_risk_employees(sdk, profile, csv_file):
    """Takes a csv file in the form `user_id,departure_date` with each row representing an 
    employee and adds each employee to the departing employee detection list in a bulk fasion.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        profile (Code42Profile): The profile under which to execute this command.
        csv_file (_io.TextIOWrapper): The csv containing rows of users.
    """
    processor = BulkProcessor(
        csv_file, lambda **kwargs: add_high_risk_employee(sdk, profile, **kwargs), u"user_id"
    )
    processor.run()
