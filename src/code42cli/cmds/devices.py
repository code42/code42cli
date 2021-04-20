from datetime import date

import click
import numpy as np
from pandas import concat
from pandas import DataFrame
from pandas import json_normalize
from pandas import Series
from pandas import to_datetime
from py42 import exceptions
from py42.exceptions import Py42NotFoundError

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.click_ext.types import MagicDate
from code42cli.date_helper import round_datetime_to_day_end
from code42cli.date_helper import round_datetime_to_day_start
from code42cli.errors import Code42CLIError
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import OutputFormatter


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def devices(state):
    """Manage devices within your Code42 environment."""
    pass


device_guid_argument = click.argument(
    "device-guid", type=str, callback=lambda ctx, param, arg: _verify_guid_type(arg),
)


def change_device_name_option(help_msg):
    return click.option(
        "--change-device-name",
        required=False,
        is_flag=True,
        default=False,
        help=help_msg,
    )


DATE_FORMAT = "%Y-%m-%d"
purge_date_option = click.option(
    "--purge-date",
    required=False,
    type=click.DateTime(formats=[DATE_FORMAT]),
    default=None,
    help="The date on which the archive should be purged from cold storage in yyyy-MM-dd format. "
    "If not provided, the date will be set according to the appropriate organization settings.",
)


@devices.command()
@device_guid_argument
@change_device_name_option(
    "Prepend 'deactivated_<current_date>' to the name of the device if deactivation is successful."
)
@purge_date_option
@sdk_options()
def deactivate(state, device_guid, change_device_name, purge_date):
    """Deactivate a device within Code42. Requires the device GUID to deactivate."""
    _deactivate_device(state.sdk, device_guid, change_device_name, purge_date)


@devices.command()
@device_guid_argument
@sdk_options()
def reactivate(state, device_guid):
    """Reactivate a device within Code42. Requires the device GUID to reactivate."""
    _reactivate_device(state.sdk, device_guid)


def _deactivate_device(sdk, device_guid, change_device_name, purge_date):
    try:
        device = _change_device_activation(sdk, device_guid, "deactivate")
    except exceptions.Py42BadRequestError:
        raise Code42CLIError(
            "The device with GUID '{}' is in legal hold.".format(device_guid)
        )
    if purge_date:
        _update_cold_storage_purge_date(sdk, device_guid, purge_date)
    if change_device_name and not device.data["name"].startswith("deactivated_"):
        _change_device_name(
            sdk,
            device_guid,
            "deactivated_"
            + date.today().strftime("%Y-%m-%d")
            + "_"
            + device.data["name"],
        )


def _reactivate_device(sdk, device_guid):
    _change_device_activation(sdk, device_guid, "reactivate")


def _change_device_activation(sdk, device_guid, cmd_str):
    try:
        device = sdk.devices.get_by_guid(device_guid)
        device_id = device.data["computerId"]
        if cmd_str == "reactivate":
            sdk.devices.reactivate(device_id)
        elif cmd_str == "deactivate":
            sdk.devices.deactivate(device_id)
        return device
    except exceptions.Py42NotFoundError:
        raise Code42CLIError(
            "The device with GUID '{}' was not found.".format(device_guid)
        )
    except exceptions.Py42ForbiddenError:
        raise Code42CLIError(
            "Unable to {} the device with GUID '{}'.".format(cmd_str, device_guid)
        )


def _verify_guid_type(device_guid):
    if device_guid is None:
        return
    try:
        int(device_guid)
        return device_guid
    except ValueError:
        raise Code42CLIError("Not a valid GUID.")


def _update_cold_storage_purge_date(sdk, guid, purge_date):
    archives_response = sdk.archive.get_all_by_device_guid(guid)
    archive_guid_list = [
        archive["archiveGuid"]
        for page in archives_response
        for archive in page["archives"]
        if archive["format"] != "ARCHIVE_V2"
    ]
    for archive_guid in archive_guid_list:
        sdk.archive.update_cold_storage_purge_date(
            archive_guid, purge_date.strftime("%Y-%m-%d")
        )


def _change_device_name(sdk, guid, name):
    device_settings = sdk.devices.get_settings(guid)
    device_settings.name = name
    sdk.devices.update_settings(device_settings)


@devices.command()
@device_guid_argument
@sdk_options()
def show(state, device_guid):
    """Print individual device details. Requires device GUID."""

    formatter = OutputFormatter(OutputFormat.TABLE, _device_info_keys_map())
    backup_set_formatter = OutputFormatter(OutputFormat.TABLE, _backup_set_keys_map())
    device_info = _get_device_info(state.sdk, device_guid)
    formatter.echo_formatted_list([device_info])
    backup_usage = device_info.get("backupUsage")
    if backup_usage:
        click.echo()
        backup_set_formatter.echo_formatted_list(backup_usage)


def _device_info_keys_map():
    return {
        "name": "Name",
        "osHostname": "Hostname",
        "guid": "GUID",
        "status": "Status",
        "lastConnected": "Last Connected Date",
        "productVersion": "Code42 Version",
        "osName": "Operating System",
        "osVersion": "Operating System Version",
    }


def _backup_set_keys_map():
    return {
        "targetComputerName": "Destination",
        "lastBackup": "Last Backup Activity",
        "lastCompleted": "Last Completed Backup",
        "archiveBytes": "Archive Size in Bytes",
        "archiveGuid": "Archive GUID",
    }


def _get_device_info(sdk, device_guid):
    return sdk.devices.get_by_guid(device_guid, include_backup_usage=True).data


active_option = click.option(
    "--active",
    is_flag=True,
    help="Limits results to only active devices.",
    default=None,
)
inactive_option = click.option(
    "--inactive",
    is_flag=True,
    help="Limits results to only deactivated devices.",
    cls=incompatible_with("active"),
)
org_uid_option = click.option(
    "--org-uid",
    required=False,
    type=str,
    default=None,
    help="Limit devices to only those in the organization you specify. "
    "Note that child organizations will be included.",
)

include_usernames_option = click.option(
    "--include-usernames",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Add the username associated with a device to the output.",
)


@devices.command(name="list")
@active_option
@inactive_option
@org_uid_option
@click.option(
    "--include-backup-usage",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Return backup usage information for each device (may significantly lengthen the size "
    "of the return).",
)
@include_usernames_option
@click.option(
    "--include-settings",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Include device settings in output.",
)
@click.option(
    "--include-legal-hold-membership",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Include legal hold membership in output.",
)
@click.option(
    "--include-total-storage",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Include backup archive count and total storage in output.",
)
@click.option(
    "--exclude-most-recently-connected",
    type=int,
    help="Filter out the N most recently connected devices per user. "
    "Useful for identifying duplicate and/or replaced devices that are no longer needed across "
    "an environment. If a user has 2 devices and N=1, the one device with the most recent "
    "'lastConnected' date will not show up in the result list.",
)
@click.option(
    "--last-connected-before",
    type=MagicDate(rounding_func=round_datetime_to_day_start),
    help=f"Include devices only when the 'lastConnected' field is after the provided value. {MagicDate.HELP_TEXT}",
)
@click.option(
    "--last-connected-after",
    type=MagicDate(rounding_func=round_datetime_to_day_end),
    help="Include devices only when 'lastConnected' field is after the provided value. "
    "Argument format options are the same as --last-connected-before.",
)
@click.option(
    "--created-before",
    type=MagicDate(rounding_func=round_datetime_to_day_start),
    help="Include devices only when 'creationDate' field is less than the provided value. "
    "Argument format options are the same as --last-connected-before.",
)
@click.option(
    "--created-after",
    type=MagicDate(rounding_func=round_datetime_to_day_end),
    help="Include devices only when 'creationDate' field is greater than the provided value. "
    "Argument format options are the same as --last-connected-before.",
)
@format_option
@sdk_options()
def list_devices(
    state,
    active,
    inactive,
    org_uid,
    include_backup_usage,
    include_usernames,
    include_settings,
    include_legal_hold_membership,
    include_total_storage,
    exclude_most_recently_connected,
    last_connected_after,
    last_connected_before,
    created_after,
    created_before,
    format,
):
    """Get information about many devices."""
    if inactive:
        active = False
    columns = [
        "computerId",
        "guid",
        "name",
        "osHostname",
        "status",
        "lastConnected",
        "creationDate",
        "productVersion",
        "osName",
        "osVersion",
        "userUid",
    ]
    df = _get_device_dataframe(
        state.sdk,
        columns,
        active,
        org_uid,
        (include_backup_usage or include_total_storage),
    )
    if last_connected_after:
        df = df.loc[to_datetime(df.lastConnected) > last_connected_after]
    if last_connected_before:
        df = df.loc[to_datetime(df.lastConnected) < last_connected_before]
    if created_after:
        df = df.loc[to_datetime(df.creationDate) > created_after]
    if created_before:
        df = df.loc[to_datetime(df.creationDate) < created_before]
    if exclude_most_recently_connected:
        most_recent = (
            df.sort_values(["userUid", "lastConnected"], ascending=False)
            .groupby("userUid")
            .head(exclude_most_recently_connected)
        )
        df = df.drop(most_recent.index)
    if include_total_storage:
        df = _add_storage_totals_to_dataframe(df, include_backup_usage)
    if include_settings:
        df = _add_settings_to_dataframe(state.sdk, df)
    if include_usernames:
        df = _add_usernames_to_device_dataframe(state.sdk, df)
    if include_legal_hold_membership:
        df = _add_legal_hold_membership_to_device_dataframe(state.sdk, df)
    if df.empty:
        click.echo("No results found.")
    else:
        formatter = DataFrameOutputFormatter(format)
        formatter.echo_formatted_dataframe(df)


def _add_legal_hold_membership_to_device_dataframe(sdk, df):
    columns = ["legalHold.legalHoldUid", "legalHold.name", "user.userUid"]

    legal_hold_member_dataframe = (
        json_normalize(list(_get_all_active_hold_memberships(sdk)))[columns]
        .groupby(["user.userUid"])
        .agg(",".join)
        .rename(
            {
                "legalHold.legalHoldUid": "legalHoldUid",
                "legalHold.name": "legalHoldName",
            },
            axis=1,
        )
    )
    df = df.merge(
        legal_hold_member_dataframe,
        how="left",
        left_on="userUid",
        right_on="user.userUid",
    )

    df.loc[df["status"] == "Deactivated", ["legalHoldUid", "legalHoldName"]] = np.nan

    return df


def _get_all_active_hold_memberships(sdk):
    for page in sdk.legalhold.get_all_matters(active=True):
        for matter in page["legalHolds"]:
            for _page in sdk.legalhold.get_all_matter_custodians(
                legal_hold_uid=matter["legalHoldUid"], active=True
            ):
                yield from _page["legalHoldMemberships"]


def _get_device_dataframe(
    sdk, columns, active=None, org_uid=None, include_backup_usage=False
):
    devices_generator = sdk.devices.get_all(
        active=active, include_backup_usage=include_backup_usage, org_uid=org_uid
    )
    devices_list = []
    if include_backup_usage:
        columns.append("backupUsage")
    for page in devices_generator:
        devices_list.extend(page["computers"])
    return DataFrame.from_records(devices_list, columns=columns)


def _add_settings_to_dataframe(sdk, device_dataframe):
    macos_guids = device_dataframe.loc[
        device_dataframe["osName"] == "mac", "guid"
    ].values

    def handle_row(guid):
        try:
            full_disk_access_status = sdk.devices.get_agent_full_disk_access_state(
                guid
            ).data[
                "value"
            ]  # returns 404 error if device isn't a Mac or doesn't have full disk access
        except Py42NotFoundError:
            full_disk_access_status = False
        return {
            "guid": guid,
            "full disk access status": full_disk_access_status,
        }

    result_list = DataFrame.from_records(
        run_bulk_process(
            handle_row, macos_guids, progress_label="Getting device settings"
        )
    )
    try:
        return device_dataframe.merge(result_list, how="left", on="guid")
    except KeyError:
        return device_dataframe


def _add_usernames_to_device_dataframe(sdk, device_dataframe):
    users_generator = sdk.users.get_all()
    users_list = []
    for page in users_generator:
        users_list.extend(page["users"])
    users_dataframe = DataFrame.from_records(
        users_list, columns=["username", "userUid"]
    )
    return device_dataframe.merge(users_dataframe, how="left", on="userUid")


def _add_storage_totals_to_dataframe(df, include_backup_usage):
    df[["archiveCount", "totalStorageBytes"]] = df["backupUsage"].apply(
        _break_backup_usage_into_total_storage
    )

    if not include_backup_usage:
        df = df.drop("backupUsage", axis=1)
    return df


def _break_backup_usage_into_total_storage(backup_usage):
    total_storage = 0
    archive_count = 0
    for archive in backup_usage:
        if archive["archiveFormat"] != "ARCHIVE_V2":
            archive_count += 1
            total_storage += archive["archiveBytes"]
    return Series([archive_count, total_storage])


@devices.command()
@active_option
@inactive_option
@org_uid_option
@include_usernames_option
@format_option
@sdk_options()
def list_backup_sets(
    state, active, inactive, org_uid, include_usernames, format,
):
    """Get information about many devices and their backup sets."""
    if inactive:
        active = False
    columns = ["guid", "userUid"]
    df = _get_device_dataframe(state.sdk, columns, active, org_uid)
    if include_usernames:
        df = _add_usernames_to_device_dataframe(state.sdk, df)
    df = _add_backup_set_settings_to_dataframe(state.sdk, df)
    if df.empty:
        click.echo("No results found.")
    else:
        formatter = DataFrameOutputFormatter(format)
        formatter.echo_formatted_dataframe(df)


def _add_backup_set_settings_to_dataframe(sdk, devices_dataframe):
    rows = [{"guid": guid} for guid in devices_dataframe["guid"].values]

    def handle_row(guid):
        try:
            current_device_settings = sdk.devices.get_settings(guid)
        except Exception as e:
            return DataFrame.from_records(
                [
                    {
                        "guid": guid,
                        "ERROR": "Unable to retrieve device settings for {}: {}".format(
                            guid, e
                        ),
                    }
                ]
            )
        current_result_dataframe = DataFrame.from_records(
            [
                {
                    "guid": current_device_settings.guid,
                    "backup set name": backup_set["name"],
                    "destinations": [
                        destination for destination in backup_set.destinations.values()
                    ],
                    "included files": backup_set.included_files,
                    "excluded files": backup_set.excluded_files,
                    "filename exclusions": backup_set.filename_exclusions,
                    "locked": backup_set.locked,
                }
                for backup_set in current_device_settings.backup_sets
            ]
        )
        return current_result_dataframe

    result_list = run_bulk_process(
        handle_row, rows, progress_label="Getting device settings"
    )
    try:
        return devices_dataframe.merge(concat(result_list), how="left", on="guid")
    except KeyError:
        return devices_dataframe


@devices.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for managing devices in bulk."""
    pass


_bulk_device_activation_headers = ["guid"]


devices_generate_template = generate_template_cmd_factory(
    group_name="devices",
    commands_dict={
        "reactivate": _bulk_device_activation_headers,
        "deactivate": _bulk_device_activation_headers,
    },
    help_message="Generate the CSV template needed for bulk device commands.",
)
bulk.add_command(devices_generate_template)


@bulk.command(name="deactivate")
@read_csv_arg(headers=_bulk_device_activation_headers)
@change_device_name_option(
    "Prepend 'deactivated_<current_date>' to the name of any successfully deactivated devices."
)
@purge_date_option
@format_option
@sdk_options()
def bulk_deactivate(state, csv_rows, change_device_name, purge_date, format):
    """Deactivate all devices from the provided CSV containing a 'guid' column."""
    sdk = state.sdk
    csv_rows[0]["deactivated"] = False
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    for row in csv_rows:
        row["change_device_name"] = change_device_name
        row["purge_date"] = purge_date

    def handle_row(**row):
        try:
            _deactivate_device(
                sdk, row["guid"], row["change_device_name"], row["purge_date"]
            )
            row["deactivated"] = "True"
        except Exception as e:
            row["deactivated"] = "False: {}".format(e)
        return row

    result_rows = run_bulk_process(
        handle_row, csv_rows, progress_label="Deactivating devices:"
    )
    formatter.echo_formatted_list(result_rows)


@bulk.command(name="reactivate")
@read_csv_arg(headers=_bulk_device_activation_headers)
@format_option
@sdk_options()
def bulk_reactivate(state, csv_rows, format):
    """Reactivate all devices from the provided CSV containing a 'guid' column."""
    sdk = state.sdk
    csv_rows[0]["reactivated"] = False
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})

    def handle_row(**row):
        try:
            _reactivate_device(sdk, row["guid"])
            row["reactivated"] = "True"
        except Exception as e:
            row["reactivated"] = "False: {}".format(e)
        return row

    result_rows = run_bulk_process(
        handle_row, csv_rows, progress_label="Reactivating devices:"
    )
    formatter.echo_formatted_list(result_rows)
