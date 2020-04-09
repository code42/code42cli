from code42cli.bulk import generate_template
from code42cli.commands import Command


def load_subcommands():
    init_csv = Command(
        u"init-csv",
        u"Generates the necessary csv template needed for bulk adding users.",
        handler=create_csv_file,
    )

    return [init_csv]


def create_csv_file(path=None):
    generate_template(add_high_risk_user, path)


def add_high_risk_user(user_id, risk_factors=None):
    pass
