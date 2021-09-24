import click
from py42.clients.trustedactivities import TrustedActivityType

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormatter

resource_id_arg = click.argument("resource-id", type=int)
type_option = click.option(
    "--type",
    help="Type of trusted activity. `DOMAIN` or `SLACK`.",
    type=click.Choice(TrustedActivityType.choices()),
)
value_option = click.option(
    "--value",
    help="The value of the trusted activity, such as the domain or Slack workspace name.",
)
description_option = click.option(
    "--description", help="The description of the trusted activity."
)


def _get_trust_header():
    return {
        "resourceId": "Resource Id",
        "type": "Type",
        "value": "Value",
        "description": "Description",
        "updatedAt": "Last Update Time",
        "updatedByUsername": "Last Updated By",
    }


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def trusted_activities(state):
    """Manage trusted activities and resources."""
    pass


@trusted_activities.command()
@click.argument("type", type=click.Choice(TrustedActivityType.choices()))
@click.argument("value")
@description_option
@sdk_options()
def create(state, type, value, description):
    """Add a trusted activity.

    VALUE is the name of the domain or Slack workspace.
    """
    state.sdk.trustedactivities.create(
        type, value, description=description,
    )


@trusted_activities.command()
@resource_id_arg
@value_option
@description_option
@sdk_options()
def update(state, resource_id, value, description):
    """Update a trusted activity.  Requires the activity's resource ID."""
    state.sdk.trustedactivities.update(
        resource_id, value=value, description=description,
    )


@trusted_activities.command()
@resource_id_arg
@sdk_options()
def remove(state, resource_id):
    """Remove a trusted activity.  Requires the activity's resource ID."""
    state.sdk.trustedactivities.delete(resource_id)


@trusted_activities.command()
@resource_id_arg
@format_option
@sdk_options()
def show(state, resource_id, format):
    """Print the details of a single trusted activity.  Requires the activity's resource ID."""
    formatter = OutputFormatter(format)
    response = state.sdk.trustedactivities.get(resource_id)
    formatter.echo_formatted_list([response.data])


@trusted_activities.command("list")
@click.option("--type", type=click.Choice(TrustedActivityType.choices()))
@format_option
@sdk_options()
def _list(state, type, format):
    """List all trusted activities."""
    pages = state.sdk.trustedactivities.get_all(type=type)
    formatter = OutputFormatter(format, _get_trust_header())
    trusted_resources = [
        resource for page in pages for resource in page["trustResources"]
    ]
    if trusted_resources:
        formatter.echo_formatted_list(trusted_resources)
    else:
        click.echo("No cases found.")


@trusted_activities.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk trusted activity actions."""
    pass


TRUST_ADD_HEADERS = [
    "type",
    "value",
    "description",
]
TRUST_UPDATE_HEADERS = [
    "resource_id",
    "value",
    "description",
]
TRUST_REMOVE_HEADERS = [
    "resource_id",
]

trusted_activities_generate_template = generate_template_cmd_factory(
    group_name="trusted_activities",
    commands_dict={
        "add": TRUST_ADD_HEADERS,
        "update": TRUST_UPDATE_HEADERS,
        "remove": TRUST_REMOVE_HEADERS,
    },
    help_message="Generate the CSV template needed for bulk trusted-activities commands",
)
bulk.add_command(trusted_activities_generate_template)


@bulk.command(name="create", help="")
@read_csv_arg(headers=TRUST_ADD_HEADERS)
@sdk_options()
def bulk_create(state, csv_rows):
    """Bulk add trusted activities."""
    sdk = state.sdk

    def handle_row(type, value, description):
        sdk.trustedactivities.create(type, value, description)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Adding trusting activities:",
    )


@bulk.command(
    name="update",
    help="Bulk update trusted activities using a CSV file with "
    f"format: {','.join(TRUST_UPDATE_HEADERS)}.",
)
@read_csv_arg(headers=TRUST_UPDATE_HEADERS)
@sdk_options()
def bulk_update(state, csv_rows):
    """Bulk update trusted activities."""
    sdk = state.sdk

    def handle_row(resource_id, value, description):
        sdk.trustedactivities.update(resource_id, value, description)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Updating trusted activities:"
    )


@bulk.command(
    name="remove",
    help="Bulk remove trusted activities using a CSV file with "
    f"format: {','.join(TRUST_REMOVE_HEADERS)}.",
)
@read_csv_arg(headers=TRUST_REMOVE_HEADERS)
@sdk_options()
def bulk_remove(state, csv_rows):
    """Bulk remove trusted activities."""
    sdk = state.sdk

    def handle_row(resource_id):
        sdk.trustedactivities.delete(resource_id)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Removing trusted activities:",
    )