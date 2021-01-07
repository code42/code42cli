from collections import OrderedDict

import click
from py42.clients.cases import CaseStatus
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42NotFoundError

from code42cli.click_ext.groups import OrderedGroup
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormatter


_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP["name"] = "Name"
_HEADER_KEYS_MAP["assignee"] = "Assignee"
_HEADER_KEYS_MAP["status"] = "Status"
_HEADER_KEYS_MAP["createdAt"] = "Creation Time"
_HEADER_KEYS_MAP["findings"] = "Notes"

name_option = click.option(
    "--name", required=False, help="Name of a case.", default=None
)
assignee_option = click.option(
    "--assignee", required=False, help="User UID of the assignee.", default=None
)
description_option = click.option(
    "--description", required=False, help="Description of the case.", default=None
)
notes_option = click.option(
    "--notes", required=False, help="Notes on the case.", default=None
)
subject_option = click.option(
    "--subject", required=False, help="User UID of a subject of a case.", default=None
)
status_option = click.option(
    "--status",
    required=False,
    help="Status of the case. `OPEN` or `CLOSED`",
    default=None,
)

case_number_arg = click.argument("case-number", type=int)
file_event_id_option = click.option(
    "--event-id", required=True, help="File event id associated to the case."
)


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
    response = state.sdk.cases.create(
        name,
        subject=subject,
        assignee=assignee,
        description=description,
        findings=notes,
    )
    return response


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


def _parse_cases(pages):
    cases = [case for page in pages for case in page["cases"]]
    if not cases:
        click.echo("No cases found.")
    return cases


@cases.command("list")
@click.option(
    "--name",
    required=False,
    help="Filter by name of a case, supports partial name matches.",
)
@click.option("--assignee", required=False, help="Filter by user UID of assignee.")
@click.option(
    "--subject", required=False, help="Filter by user UID of the subject of a case."
)
@click.option("--assignee", required=False, help="Filter by user UID of assignee.")
@click.option(
    "--created-at-begin-time",
    required=False,
    help="Fetch cases created after given date.",
)
@click.option(
    "--created-at-end-time",
    required=False,
    help="Fetch cases created before given date.",
)
@click.option(
    "--updated-at-begin-time",
    required=False,
    help="Fetch cases last updated after given date.",
)
@click.option(
    "--updated-at-end-time",
    required=False,
    help="Fetch cases last updated before given date.",
)
@click.option("--status", required=False, help="Filter cases by cast status.")
@format_option
@sdk_options()
def _list(
    state,
    name,
    assignee,
    subject,
    created_at_begin_time,
    created_at_end_time,
    updated_at_begin_time,
    updated_at_end_time,
    status,
    format,
):
    """List all the cases."""
    pages = state.sdk.cases.get_all(
        name=name,
        assignee=assignee,
        subject=subject,
        created_at_begin_time=created_at_begin_time,
        created_at_end_time=created_at_end_time,
        updated_at_begin_time=updated_at_begin_time,
        updated_at_end_time=updated_at_end_time,
        status=status,
    )
    formatter = OutputFormatter(format, _HEADER_KEYS_MAP)
    cases = _parse_cases(pages)
    if cases:
        formatter.echo_formatted_list(cases)


@cases.command()
@case_number_arg
@sdk_options()
def show(state, case_number):
    """Show case details."""
    click.echo(state.sdk.cases.get_case(case_number))


@cases.command()
@case_number_arg
@click.option(
    "--path", type=str, help="File path. Defaults to current directory", default="."
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
def file_events_list(state, case_number):
    """List all the events associated with the case."""
    try:
        response = state.sdk.cases.file_events.get_all(case_number)
    except Py42NotFoundError as err:
        click.echo("Invalid case-number.")
        raise err
    if not response["events"]:
        click.echo("No events found.")
    for event in response["events"]:
        click.echo(event)


@file_events.command("show")
@case_number_arg
@file_event_id_option
@sdk_options()
def _show(state, case_number, event_id):
    """Show event details for the given event id associated with the case."""
    try:
        click.echo(state.sdk.cases.file_events.get_event(case_number, event_id))
    except Py42NotFoundError as err:
        click.echo("Invalid case-number or event-id.")
        raise err


@file_events.command()
@case_number_arg
@file_event_id_option
@sdk_options()
def add(state, case_number, event_id):
    """Associate an event id to the case."""
    try:
        state.sdk.cases.file_events.add_event(case_number, event_id)
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
        state.sdk.cases.file_events.delete_event(case_number, event_id)
    except Py42NotFoundError as err:
        click.echo("Invalid case-number or event-id.")
        raise err
