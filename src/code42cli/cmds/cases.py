import json
import os

import click
from py42.clients.cases import CaseStatus
from py42.exceptions import Py42BadRequestError
from py42.exceptions import Py42CaseAlreadyHasEventError
from py42.exceptions import Py42NotFoundError
from py42.exceptions import Py42UpdateClosedCaseError

from code42cli.click_ext.groups import OrderedGroup
from code42cli.errors import Code42CLIError
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.options import set_begin_default_dict
from code42cli.options import set_end_default_dict
from code42cli.output_formats import OutputFormatter


case_number_arg = click.argument("case-number", type=int)
case_number_option = click.option(
    "--case-number", type=int, help="The number assigned to the case.", required=True
)
name_option = click.option("--name", help="The name of the case.",)
assignee_option = click.option(
    "--assignee", help="The UID of the user to assign to the case."
)
description_option = click.option("--description", help="The description of the case.")
findings_option = click.option("--findings", help="Any findings for the case.")
subject_option = click.option(
    "--subject", help="The user UID of the subject of the case."
)
status_option = click.option(
    "--status",
    help="Status of the case. `OPEN` or `CLOSED`.",
    type=click.Choice(CaseStatus.choices()),
)
file_event_id_option = click.option(
    "--event-id", required=True, help="The file event ID associated with the case."
)
CASES_KEYWORD = "cases"
BEGIN_DATE_DICT = set_begin_default_dict(CASES_KEYWORD)
END_DATE_DICT = set_end_default_dict(CASES_KEYWORD)


def _get_cases_header():
    return {
        "number": "Number",
        "name": "Name",
        "assignee": "Assignee",
        "status": "Status",
        "subject": "Subject",
        "createdAt": "Creation Time",
        "updatedAt": "Last Update Time",
    }


def _get_events_header():
    return {
        "eventId": "Event Id",
        "eventTimestamp": "Timestamp",
        "filePath": "Path",
        "fileName": "File",
        "exposure": "Exposure",
    }


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def cases(state):
    """Manage cases and events associated with cases."""
    pass


@cases.command()
@click.argument("name")
@assignee_option
@description_option
@findings_option
@subject_option
@sdk_options()
def create(state, name, subject, assignee, description, findings):
    """Create a new case."""
    state.sdk.cases.create(
        name,
        subject=subject,
        assignee=assignee,
        description=description,
        findings=findings,
    )


@cases.command()
@case_number_arg
@name_option
@assignee_option
@description_option
@findings_option
@subject_option
@status_option
@sdk_options()
def update(state, case_number, name, subject, assignee, description, findings, status):
    """Update case details for the given case."""
    state.sdk.cases.update(
        case_number,
        name=name,
        subject=subject,
        assignee=assignee,
        description=description,
        findings=findings,
        status=status,
    )


@cases.command("list")
@click.option(
    "--name", help="Filter by name of a case. Supports partial name matches.",
)
@click.option("--subject", help="Filter by the user UID of the subject of a case.")
@click.option("--assignee", help="Filter by the user UID of an assignee.")
@click.option("--begin-create-time", **BEGIN_DATE_DICT)
@click.option("--end-create-time", **END_DATE_DICT)
@click.option("--begin-update-time", **BEGIN_DATE_DICT)
@click.option("--end-update-time", **END_DATE_DICT)
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


def _get_file_events(sdk, case_number):
    response = sdk.cases.file_events.get_all(case_number)
    if not response["events"]:
        return None
    return json.loads(response.text)


def _display_file_events(events):
    if events:
        click.echo("\nFile Events:\n")
        click.echo(json.dumps(events, indent=4))
    else:
        click.echo("\nNo events found.")


@cases.command()
@case_number_arg
@click.option(
    "--include-file-events",
    is_flag=True,
    help="View file events associated to the case.",
)
@sdk_options()
@format_option
def show(state, case_number, format, include_file_events):
    """Show case details."""
    formatter = OutputFormatter(format)
    try:
        response = state.sdk.cases.get(case_number)
        formatter.echo_formatted_list([response.data])
        if include_file_events:
            events = _get_file_events(state.sdk, case_number)
            _display_file_events(events)
    except Py42NotFoundError:
        raise Code42CLIError("Invalid case-number {}.".format(case_number))


@cases.command()
@case_number_arg
@click.option(
    "--path",
    help="The file path where to save the PDF. Defaults to the current directory.",
    default=os.getcwd(),
)
@sdk_options()
def export(state, case_number, path):
    """Download a case detail summary as a PDF file at the given path with name <case_number>_case_summary.pdf."""
    response = state.sdk.cases.export_summary(case_number)
    file = os.path.join(path, "{}_case_summary.pdf".format(case_number))
    with open(file, "wb") as f:
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
    """List all the file events associated with the case."""
    formatter = OutputFormatter(format, _get_events_header())
    try:
        response = state.sdk.cases.file_events.get_all(case_number)
    except Py42NotFoundError:
        raise Code42CLIError("Invalid case-number.")

    if not response["events"]:
        click.echo("No events found.")
    else:
        events = [event for event in response["events"]]
        formatter.echo_formatted_list(events)


@file_events.command()
@case_number_option
@file_event_id_option
@sdk_options()
def add(state, case_number, event_id):
    """Associate a file event to a case, by event ID."""
    try:
        state.sdk.cases.file_events.add(case_number, event_id)
    except Py42UpdateClosedCaseError:
        raise
    except Py42CaseAlreadyHasEventError:
        raise
    except Py42BadRequestError:
        raise Code42CLIError("Invalid case-number or event-id.")


@file_events.command()
@case_number_option
@file_event_id_option
@sdk_options()
def remove(state, case_number, event_id):
    """Remove the associated file event from the case, by event ID."""
    try:
        state.sdk.cases.file_events.delete(case_number, event_id)
    except Py42NotFoundError:
        raise Code42CLIError("Invalid case-number or event-id.")
