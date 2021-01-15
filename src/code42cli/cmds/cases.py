import click
from py42.clients.cases import CaseStatus
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42NotFoundError

from code42cli.click_ext.groups import OrderedGroup
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormatter


case_number_arg = click.argument("case-number", type=int)
name_option = click.option("--name", help="Name of the case.",)
assignee_option = click.option("--assignee", help="User UID of the assignee.")
description_option = click.option("--description", help="Description of the case.")
notes_option = click.option("--notes", help="Notes on the case.")
subject_option = click.option("--subject", help="User UID of a subject of the case.")
status_option = click.option(
    "--status",
    help="Status of the case. `OPEN` or `CLOSED`.",
    type=click.Choice(CaseStatus.choices()),
)
file_event_id_option = click.option(
    "--event-id", required=True, help="File event id associated to the case."
)

DATE_FORMAT = "%Y-%m-%d"


def _get_cases_header():
    return {
        "number": "number",
        "name": "Name",
        "assignee": "Assignee",
        "status": "Status",
        "createdAt": "Creation Time",
        "findings": "Notes",
    }


def _get_events_header():
    return {
        "eventId": "Event Id",
        "eventTimestatmp": "Timestamp",
        "filePath": "Path",
        "fileName": "File",
        "exposure": "Exposure",
    }


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def cases(state):
    """For managing cases and events associated with cases."""
    pass


@cases.command()
@click.argument("name")
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
        findings=notes,
    )


@cases.command()
@case_number_arg
@name_option
@assignee_option
@description_option
@notes_option
@subject_option
@status_option
@sdk_options()
def update(state, case_number, name, subject, assignee, description, notes, status):
    """Update case details for the given case."""
    state.sdk.cases.update(
        case_number,
        name=name,
        subject=subject,
        assignee=assignee,
        description=description,
        findings=notes,
        status=status,
    )


@cases.command("list")
@click.option(
    "--name", help="Filter by name of a case, supports partial name matches.",
)
@click.option("--subject", help="Filter by user UID of the subject of a case.")
@click.option("--assignee", help="Filter by user UID of assignee.")
@click.option(
    "--begin-create-time", help="Fetch cases created after given date time.",
    type=click.DateTime(formats=[DATE_FORMAT]),
)
@click.option(
    "--end-create-time", help="Fetch cases created before given date time.",
    type=click.DateTime(formats=[DATE_FORMAT]),
)
@click.option(
    "--begin-update-time", help="Fetch cases last updated after given date time.",
    type=click.DateTime(formats=[DATE_FORMAT]),
)
@click.option(
    "--end-update-time", help="Fetch cases last updated before given date time.",
    type=click.DateTime(formats=[DATE_FORMAT]),
)
@click.option("--status", help="Filter cases by case status.")
@format_option
@sdk_options()
def _list(
    state,
    name,
    assignee,
    subject,
    begin_create_time,
    end_create_time,
    begin_update_time,
    end_update_time,
    status,
    format,
):
    """List all the cases."""
    pages = state.sdk.cases.get_all(
        name=name,
        assignee=assignee,
        subject=subject,
        min_create_time=begin_create_time,
        max_create_time=end_create_time,
        min_update_time=begin_update_time,
        max_update_time=end_update_time,
        status=status,
    )
    formatter = OutputFormatter(format, _get_cases_header())
    cases = [case for page in pages for case in page["cases"]]
    if cases:
        formatter.echo_formatted_list(cases)
    else:
        click.echo("No cases found.")


@cases.command()
@case_number_arg
@sdk_options()
@format_option
def show(state, case_number, format):
    """Show case details."""
    formatter = OutputFormatter(format, _get_cases_header())
    try:
        response = state.sdk.cases.get(case_number)
        formatter.echo_formatted_list([response.data])
    except Py42NotFoundError:
        click.echo("Invalid case-number {}.".format(case_number))


@cases.command()
@case_number_arg
@click.option(
    "--path", type=str, help="File path. Defaults to current directory.", default="."
)
@sdk_options()
def export(state, case_number, path):
    """Download case detail summary in a pdf file at the given path with name <case_number>_case_summary.pdf."""
    response = state.sdk.cases.export_summary(case_number)
    with open("{}/{}_case_summary.pdf".format(path, case_number), "wb") as f:
        f.write(response.content)


@cases.group(cls=OrderedGroup)
@sdk_options()
def file_events(state):
    """Fetch file events associated with the case."""
    pass


@file_events.command("list")
@case_number_arg
@sdk_options()
@format_option
def file_events_list(state, case_number, format):
    """List all the events associated with the case."""
    formatter = OutputFormatter(format, _get_events_header())
    try:
        response = state.sdk.cases.file_events.get_all(case_number)
    except Py42NotFoundError as err:
        click.echo("Invalid case-number.")
        raise err
    if not response["events"]:
        click.echo("No events found.")
    for event in response["events"]:
        events = [event for event in response["events"]]
        formatter.echo_formatted_list(events)


@file_events.command("show")
@case_number_arg
@file_event_id_option
@sdk_options()
@format_option
def _show(state, case_number, event_id, format):
    """Show event details for the given event id associated with the case."""
    formatter = OutputFormatter(format, _get_events_header())
    try:
        response = state.sdk.cases.file_events.get(case_number, event_id)
        formatter.echo_formatted_list([response.data])
    except Py42NotFoundError as err:
        click.echo("Invalid case-number or event-id.")
        raise err


@file_events.command()
@case_number_arg
@file_event_id_option
@sdk_options()
def add(state, case_number, event_id):
    """Associate an event id to a case."""
    try:
        state.sdk.cases.file_events.add(case_number, event_id)
    except Py42BadRequestError as err:
        click.echo("Invalid case-number or event-id.")
        raise err


@file_events.command()
@case_number_arg
@file_event_id_option
@sdk_options()
def remove(state, case_number, event_id):
    """Remove the associated event id from the case."""
    try:
        state.sdk.cases.file_events.delete(case_number, event_id)
    except Py42NotFoundError as err:
        click.echo("Invalid case-number or event-id.")
        raise err
