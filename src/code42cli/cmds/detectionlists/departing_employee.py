from code42cli.bulk import generate_template, BulkProcessor
from code42cli.commands import Command


def load_subcommands():
    init_csv = Command(
        u"init-csv",
        u"Generates the necessary csv template needed for bulk adding users.",
        handler=create_csv_file,
    )

    add = Command(
        u"add",
        u"Add a user to the departing employee detection list.",
        handler=add_departing_employee,
    )

    return [init_csv, add]


def create_csv_file(path=None):
    generate_template(add_departing_employee, path)


def add_departing_employee(sdk, profile, user_id, departure_date=None):
    # sdk.detectionlists.departing_employee.create(user_id, departure_date=departure_date)
    pass


def bulk_add_departing_employees(sdk, profile, csv):
    processor = BulkProcessor(
        csv, lambda **kwargs: add_departing_employee(sdk, profile, **kwargs), u"user_id"
    )
    processor.run()
