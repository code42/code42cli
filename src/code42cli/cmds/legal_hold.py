import json
from collections import OrderedDict
from functools import lru_cache
from pprint import pformat

import click
from click import echo
from pandas import DataFrame

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.cmds.shared import get_user_id
from code42cli.errors import UserNotInLegalHoldError
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import OutputFormatter
from code42cli.util import format_string_list_to_columns


_MATTER_KEYS_MAP = OrderedDict()
_MATTER_KEYS_MAP["legalHoldUid"] = "Matter ID"
_MATTER_KEYS_MAP["name"] = "Name"
_MATTER_KEYS_MAP["description"] = "Description"
_MATTER_KEYS_MAP["creator_username"] = "Creator"
_MATTER_KEYS_MAP["creationDate"] = "Creation Date"


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def legal_hold(state):
    """For adding and removing custodians from legal hold matters."""
    pass


matter_id_option = click.option(
    "-m",
    "--matter-id",
    required=True,
    type=str,
    help="Identification number of the legal hold matter the custodian will be added to.",
)
user_id_option = click.option(
    "-u",
    "--username",
    required=True,
    type=str,
    help="The username of the custodian to add to the matter.",
)


@legal_hold.command()
@matter_id_option
@user_id_option
@sdk_options()
def add_user(state, matter_id, username):
    """Add a custodian to a legal hold matter."""
    _add_user_to_legal_hold(state.sdk, matter_id, username)


@legal_hold.command()
@matter_id_option
@user_id_option
@sdk_options()
def remove_user(state, matter_id, username):
    """Release a custodian from a legal hold matter."""
    _remove_user_from_legal_hold(state.sdk, matter_id, username)


@legal_hold.command("list")
@format_option
@sdk_options()
def _list(state, format=None):
    """Fetch existing legal hold matters."""
    formatter = OutputFormatter(format, _MATTER_KEYS_MAP)
    matters = _get_all_active_matters(state.sdk)
    if matters:
        formatter.echo_formatted_list(matters)


@legal_hold.command()
@click.argument("matter-id")
@click.option(
    "--include-inactive",
    is_flag=True,
    help="View all custodians associated with the legal hold matter, "
    "including inactive custodians.",
)
@click.option(
    "--include-policy",
    is_flag=True,
    help="View details of the preservation policy associated with the legal hold matter.",
)
@click.option(
    "--include-devices",
    is_flag=True,
    help="View devices and storage associated with legal hold custodians.",
)
@sdk_options()
def show(
    state,
    matter_id,
    include_inactive=False,
    include_policy=False,
    include_devices=False,
):
    """Display details of a given legal hold matter."""
    matter = _check_matter_is_accessible(state.sdk, matter_id)
    matter["creator_username"] = matter["creator"]["username"]
    matter = json.loads(matter.text)

    # if `active` is None then all matters (whether active or inactive) are returned. True returns
    # only those that are active.
    active = None if include_inactive else True
    memberships = _get_legal_hold_memberships_for_matter(
        state.sdk, matter_id, active=active
    )

    formatter = OutputFormatter(OutputFormat.TABLE, _MATTER_KEYS_MAP)
    formatter.echo_formatted_list([matter])

    users = [
        [member["active"], member["user"]["userUid"], member["user"]["username"]]
        for member in memberships
    ]

    usernames = [user[2] for user in users if user[0] is True]
    _print_matter_members(usernames, member_type="active")
    if include_inactive:
        usernames = [user[2] for user in users if user[0] is not True]
        _print_matter_members(usernames, member_type="inactive")

    if include_devices:
        user_dataframe = _build_user_dataframe(users)
        devices_dataframe = _merge_matter_members_with_devices(
            state.sdk, user_dataframe
        )
        if len(devices_dataframe.index) > 0:
            echo("\nMatter Members and Devices:\n")
            click.echo(devices_dataframe.to_csv())
            echo(_print_storage_by_org(devices_dataframe))
        else:
            echo("\nNo devices associated with matter.\n")

    if include_policy:
        _get_and_print_preservation_policy(state.sdk, matter["holdPolicyUid"])
        echo("")


@legal_hold.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for executing bulk legal hold actions."""
    pass


LEGAL_HOLD_CSV_HEADERS = ["matter_id", "username"]


legal_hold_generate_template = generate_template_cmd_factory(
    group_name="legal_hold",
    commands_dict={"add": LEGAL_HOLD_CSV_HEADERS, "remove": LEGAL_HOLD_CSV_HEADERS},
)
bulk.add_command(legal_hold_generate_template)


@bulk.command(
    name="add",
    help="Bulk add custodians to legal hold matters using a CSV file. CSV file format: {}".format(
        ",".join(LEGAL_HOLD_CSV_HEADERS)
    ),
)
@read_csv_arg(headers=LEGAL_HOLD_CSV_HEADERS)
@sdk_options()
def bulk_add(state, csv_rows):
    sdk = state.sdk

    def handle_row(matter_id, username):
        _add_user_to_legal_hold(sdk, matter_id, username)

    run_bulk_process(handle_row, csv_rows, progress_label="Adding users to legal hold:")


@bulk.command(
    help="Bulk release custodians from legal hold matters using a CSV file. CSV file format: {}".format(
        ",".join(LEGAL_HOLD_CSV_HEADERS)
    )
)
@read_csv_arg(headers=LEGAL_HOLD_CSV_HEADERS)
@sdk_options()
def remove(state, csv_rows):
    sdk = state.sdk

    def handle_row(matter_id, username):
        _remove_user_from_legal_hold(sdk, matter_id, username)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Removing users from legal hold:"
    )


def _add_user_to_legal_hold(sdk, matter_id, username):
    user_id = get_user_id(sdk, username)
    _check_matter_is_accessible(sdk, matter_id)
    sdk.legalhold.add_to_matter(user_id, matter_id)


def _remove_user_from_legal_hold(sdk, matter_id, username):
    _check_matter_is_accessible(sdk, matter_id)
    membership_id = _get_legal_hold_membership_id_for_user_and_matter(
        sdk, username, matter_id
    )
    sdk.legalhold.remove_from_matter(membership_id)


def _get_and_print_preservation_policy(sdk, policy_uid):
    preservation_policy = sdk.legalhold.get_policy_by_uid(policy_uid)
    echo("\nPreservation Policy:\n")
    echo(pformat(json.loads(preservation_policy.text)))


def _get_legal_hold_membership_id_for_user_and_matter(sdk, username, matter_id):
    user_id = get_user_id(sdk, username)
    memberships = _get_legal_hold_memberships_for_matter(sdk, matter_id, active=True)
    for member in memberships:
        if member["user"]["userUid"] == user_id:
            return member["legalHoldMembershipUid"]
    raise UserNotInLegalHoldError(username, matter_id)


def _get_legal_hold_memberships_for_matter(sdk, matter_id, active=True):
    memberships_generator = sdk.legalhold.get_all_matter_custodians(
        legal_hold_uid=matter_id, active=active
    )
    memberships = [
        member
        for page in memberships_generator
        for member in page["legalHoldMemberships"]
    ]
    return memberships


def _get_all_active_matters(sdk):
    matters_generator = sdk.legalhold.get_all_matters()
    matters = [
        matter
        for page in matters_generator
        for matter in page["legalHolds"]
        if matter["active"]
    ]
    for matter in matters:
        matter["creator_username"] = matter["creator"]["username"]
    return matters


def _print_matter_members(username_list, member_type="active"):
    if username_list:
        echo("\n{} matter members:\n".format(member_type.capitalize()))
        format_string_list_to_columns(username_list)
    else:
        echo("No {} matter members.\n".format(member_type))


def _merge_matter_members_with_devices(sdk, user_dataframe):
    devices_generator = sdk.devices.get_all(active="true", include_backup_usage=True)
    device_list = _get_total_archive_bytes_per_device(devices_generator)
    devices_dataframe = DataFrame.from_records(
        device_list,
        columns=[
            "userUid",
            "guid",
            "name",
            "osHostname",
            "status",
            "alertStates",
            "orgId",
            "lastConnected",
            "version",
            "archiveBytes",
        ],
    )
    return user_dataframe.merge(
        devices_dataframe, how="inner", on="userUid"
    ).reset_index(drop=True)


def _build_user_dataframe(users):
    user_dataframe = DataFrame.from_records(
        users, columns=["activeMembership", "userUid", "username"]
    )
    return user_dataframe


def _get_total_archive_bytes_per_device(devices_generator):
    device_list = [device for page in devices_generator for device in page["computers"]]
    for i in device_list:
        archive_bytes = [archive["archiveBytes"] for archive in i["backupUsage"]]
        i["archiveBytes"] = sum(archive_bytes)
    return device_list


def _print_storage_by_org(devices_dataframe):
    echo("\nLegal Hold Storage by Org\n")
    devices_dataframe = devices_dataframe.filter(["orgId", "archiveBytes"])
    return devices_dataframe.groupby("orgId").sum()


@lru_cache(maxsize=None)
def _check_matter_is_accessible(sdk, matter_id):
    return sdk.legalhold.get_matter_by_uid(matter_id)
