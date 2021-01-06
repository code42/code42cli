import click
from code42cli.click_ext.groups import OrderedGroup
from code42cli.options import sdk_options


name_option = click.option("--name", required=False, help="Name of a case.", default=None)
assignee_option = click.option("--assignee", required=False, help="User UID of the assignee.", default=None)
description_option = click.option("--description", required=False, help="Description of the case.", default=None)
notes_option = click.option("--notes", required=False, help="Notes on the case.", default=None)
subject_option = click.option("--subject", required=False, help="User UID of a subject of a case.", default=None)

case_number_arg = click.argument("case-number", type=int)
file_event_id_option = click.option("--event-id", required=True, help="File event id associated to the case.")


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def cases(state):
    """For managing cases and events associated with cases."""
    pass


@cases.command()
@click.argument("name", type=str)
@assignee_option
@description_option
@notes_option
@subject_option
@sdk_options()
def create(state, name, subject, assignee, description, notes):
    """Create a new case."""
    state.sdk.cases.create(
        name,
        subject=subject,
        assignee=assignee,
        description=description,
        findings=notes
    )


@cases.command()
@name_option
@assignee_option
@description_option
@notes_option
@subject_option
@sdk_options()
def update(state, name, subject, assignee, description, notes):
    """Update case details for the given case."""
    state.sdk.cases.update(
        name,
        subject=subject,
        assignee=assignee,
        description=description,
        findings=notes
    )


@cases.command("list")
@click.option("--name", required=False, help="Filter by name of a case, supports partial name matches.")
@click.option("--assignee", required=False, help="Filter by user UID of assignee.")
@click.option("--subject", required=False, help="Filter by user UID of the subject of a case.")
@click.option("--assignee", required=False, help="Filter by user UID of assignee.")
@click.option("--create-start-date", required=False, help="Fetch cases created after given date.")
@click.option("--create-end-date", required=False, help="Fetch cases created before given date.")
@click.option("--update-start-date", required=False, help="Fetch cases last updated after given date.")
@click.option("--update-end-date", required=False, help="Fetch cases last updated before given date.")
@sdk_options()
def _list(
    state, name, assignee, subject, create_start_date, create_end_date, update_start_date, update_end_date
):
    """List all the cases."""
    pass


@cases.command()
@case_number_arg
@sdk_options()
def show(state, case_number):
    """Show case details."""
    state.sdk.cases.get_case(case_number)


@cases.command()
@case_number_arg
@sdk_options()
def export(state, case_number):
    """Download case detail summary."""
    state.sdk.cases.export_summary(case_number)


@cases.group(cls=OrderedGroup)
@sdk_options()
def file_events(state):
    """Fetch file events associated with the case."""
    pass


@file_events.command("list")
@case_number_arg
@sdk_options()
def file_events_list(state, case_number):
    """List all the events associated with the case."""
    state.sdk.cases.file_events.get_all_events(case_number)


@file_events.command("show")
@case_number_arg
@file_event_id_option
@sdk_options()
def _show(state, case_number):
    """Show event details for the given event id associated with the case."""
    state.sdk.cases.file_events.get_event(case_number, event_id)


@file_events.command()
@case_number_arg
@file_event_id_option
@sdk_options()
def add(state, case_number, event_id):
    """Associate an event id to the case."""
    state.sdk.cases.file_events.add_event(case_number, event_id)


@file_events.command()
@case_number_arg
@file_event_id_option
@sdk_options()
def remove(state, case_number, event_id):
    """Remove the associated event id from the case."""
    state.sdk.cases.file_events.delete_event(case_number, event_id)
