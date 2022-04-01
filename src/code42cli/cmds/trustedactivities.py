import click
from py42.clients.trustedactivities import TrustedActivityType

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.errors import Code42CLIError
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormatter

resource_id_arg = click.argument("resource-id", type=int)
type_option = click.option(
    "--type",
    help=f"Type of trusted activity. Valid types include {', '.join(TrustedActivityType.choices())}.",
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
        "updatedByUsername": "Last Updated By (Username)",
        "updatedByUserUid": "Last updated By (UserUID)",
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
    """Create a trusted activity.

    VALUE is the name of the domain or Slack workspace.
    """
    state.sdk.trustedactivities.create(
        type,
        value,
        description=description,
    )


@trusted_activities.command()
@resource_id_arg
@value_option
@description_option
@sdk_options()
def update(state, resource_id, value, description):
    """Update a trusted activity.  Requires the activity's resource ID."""
    state.sdk.trustedactivities.update(
        resource_id,
        value=value,
        description=description,
    )


@trusted_activities.command()
@resource_id_arg
@sdk_options()
def remove(state, resource_id):
    """Remove a trusted activity.  Requires the activity's resource ID."""
    state.sdk.trustedactivities.delete(resource_id)


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
        click.echo("No trusted activities found.")


@trusted_activities.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk trusted activity actions."""
    pass


TRUST_CREATE_HEADERS = [
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
        "create": TRUST_CREATE_HEADERS,
        "update": TRUST_UPDATE_HEADERS,
        "remove": TRUST_REMOVE_HEADERS,
    },
    help_message="Generate the CSV template needed for bulk trusted-activities commands",
)
bulk.add_command(trusted_activities_generate_template)


@bulk.command(
    name="create",
    help="Bulk create trusted activities using a CSV file with "
    f"format: {','.join(TRUST_CREATE_HEADERS)}.\b\n\n"
    f"Available `type` values are: {'|'.join(TrustedActivityType.choices())}",
)
@read_csv_arg(headers=TRUST_CREATE_HEADERS)
@sdk_options()
def bulk_create(state, csv_rows):
    """Bulk create trusted activities."""
    sdk = state.sdk

    def handle_row(type, value, description):
        if type not in TrustedActivityType.choices():
            message = f"Invalid type {type}, valid types include {', '.join(TrustedActivityType.choices())}."
            raise Code42CLIError(message)
        if type is None:
            message = "'type' is a required field to create a trusted activity."
            raise Code42CLIError(message)
        if value is None:
            message = "'value' is a required field to create a trusted activity."
            raise Code42CLIError(message)
        sdk.trustedactivities.create(type, value, description)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Creating trusting activities:",
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
        if resource_id is None:
            message = "'resource_id' is a required field to update a trusted activity."
            raise Code42CLIError(message)
        _check_resource_id_type(resource_id)
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
        if resource_id is None:
            message = "'resource_id' is a required field to remove a trusted activity."
            raise Code42CLIError(message)
        _check_resource_id_type(resource_id)
        sdk.trustedactivities.delete(resource_id)

    run_bulk_process(
        handle_row,
        csv_rows,
        progress_label="Removing trusted activities:",
    )


def _check_resource_id_type(resource_id):
    def raise_error(resource_id):
        message = f"Invalid resource ID {resource_id}.  Must be an integer."
        raise Code42CLIError(message)

    try:
        if not float(resource_id).is_integer():
            raise_error(resource_id)
    except ValueError:
        raise_error(resource_id)
