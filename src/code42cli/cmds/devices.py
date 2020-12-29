from datetime import date
from datetime import datetime

import click
from pandas import concat
from pandas import DataFrame
from pandas import to_datetime
from pandas import to_timedelta
from py42 import exceptions
from py42.exceptions import Py42NotFoundError

from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.errors import Code42CLIError
from code42cli.file_readers import read_csv_arg
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter
from code42cli.output_formats import OutputFormatter


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def devices(state):
    """For managing devices within your Code42 environment."""
    pass


device_guid_argument = click.argument("device-guid", type=str)

change_device_name_option = click.option(
    "--change-device-name",
    required=False,
    is_flag=True,
    default=False,
    help="""Prepend "deactivated_" and today's date to the name of any
    deactivated devices.""",
)

DATE_FORMAT = "%Y-%m-%d"
purge_date_option = click.option(
    "--purge-date",
    required=False,
    type=click.DateTime(formats=[DATE_FORMAT]),
    default=None,
    help="""The date on which the archive should be purged from cold storage in yyyy-MM-dd format.
    If not provided, the date will be set according to the appropriate org settings.""",
)


@devices.command()
@device_guid_argument
@change_device_name_option
@purge_date_option
@sdk_options()
def deactivate(state, device_guid, change_device_name, purge_date):
    """Deactivate a device within Code42. Requires the device GUID to deactivate."""
    _deactivate_device(state.sdk, device_guid, change_device_name, purge_date)


def _deactivate_device(sdk, device_guid, change_device_name, purge_date):
    device = sdk.devices.get_by_guid(device_guid)
    try:
        sdk.devices.deactivate(device.data["computerId"])
    except exceptions.Py42BadRequestError:
        raise Code42CLIError("The device {} is in legal hold.".format(device_guid))
    except exceptions.Py42NotFoundError:
        raise Code42CLIError("The device {} was not found.".format(device_guid))
    except exceptions.Py42ForbiddenError:
        raise Code42CLIError("Unable to deactivate {}.".format(device_guid))
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
@format_option
@sdk_options()
def show(state, device_guid, format=None):
    """Print device info. Requires device GUID."""

    formatter = OutputFormatter(format, _device_info_keys_map())
    backup_set_formatter = OutputFormatter(format, _backup_set_keys_map())
    device_info = _get_device_info(state.sdk, device_guid)
    formatter.echo_formatted_list([device_info])
    click.echo()
    backup_set_formatter.echo_formatted_list(device_info["backupUsage"])


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
    required=False,
    type=bool,
    is_flag=True,
    default=None,
    help="Get only active or deactivated devices. Defaults to getting all devices.",
)

org_uid_option = click.option(
    "--org-uid",
    required=False,
    type=str,
    default=None,
    help="""Limit devices to only the ones in the org you specify.
    Note that child orgs will be included.""",
)

include_usernames_option = click.option(
    "--include-usernames",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Add the username associated with a device to the output.",
)


@devices.command(name="list", help="Get information about many devices")
@active_option
@click.option(
    "--days-since-last-connected",
    required=False,
    type=int,
    help="Return only devices that have not connected in the number of days specified.",
)
@org_uid_option
@click.option(
    "--drop-most-recent",
    required=False,
    type=int,
    help="""Will drop the X most recently connected devices for each user from the
    result list where X is the number you provide as this argument. Can be used to
    avoid passing the most recently connected device for a user to the deactivate command.""",
)
@click.option(
    "--include-backup-usage",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="""Return backup usage information for each device
    (may significantly lengthen the size of the return).""",
)
@include_usernames_option
@click.option(
    "--include-settings",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="""Include device settings in output.""",
)
@format_option
@sdk_options()
def list_devices(
    state,
    active,
    days_since_last_connected,
    drop_most_recent,
    org_uid,
    include_backup_usage,
    include_usernames,
    include_settings,
    format,
):
    """Outputs a list of all devices."""
    columns = [
        "computerId",
        "guid",
        "name",
        "osHostname",
        "status",
        "lastConnected",
        "productVersion",
        "osName",
        "osVersion",
        "userUid",
    ]
    devices_dataframe = _get_device_dataframe(
        state.sdk, columns, active, org_uid, include_backup_usage
    )
    if drop_most_recent:
        devices_dataframe = _drop_n_devices_per_user(
            devices_dataframe, drop_most_recent
        )
    if days_since_last_connected:
        devices_dataframe = _drop_devices_which_have_not_connected_in_some_number_of_days(
            devices_dataframe, days_since_last_connected
        )
    if include_settings:
        devices_dataframe = _add_settings_to_dataframe(state.sdk, devices_dataframe)
    if include_usernames:
        devices_dataframe = _add_usernames_to_device_dataframe(
            state.sdk, devices_dataframe
        )
    formatter = DataFrameOutputFormatter(format)
    formatter.echo_formatted_dataframe(devices_dataframe)


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


def _drop_devices_which_have_not_connected_in_some_number_of_days(
    devices_dataframe, days_since_last_connected
):
    utc_now = to_datetime(datetime.utcnow(), utc=True)
    devices_last_connected_dates = to_datetime(devices_dataframe["lastConnected"])
    days_since_last_connected_delta = to_timedelta(
        days_since_last_connected, unit="days"
    )
    return devices_dataframe.loc[
        utc_now - devices_last_connected_dates > days_since_last_connected_delta, :,
    ]


def _drop_n_devices_per_user(
    device_dataframe,
    number_to_drop,
    sort_field="lastConnected",
    sort_ascending=False,
    group_field="userUid",
):
    return (
        device_dataframe.sort_values(by=sort_field, ascending=sort_ascending)
        .drop(device_dataframe.groupby(group_field).head(number_to_drop).index)
        .reset_index(drop=True)
    )


def _add_usernames_to_device_dataframe(sdk, device_dataframe):
    users_generator = sdk.users.get_all()
    users_list = []
    for page in users_generator:
        users_list.extend(page["users"])
    users_dataframe = DataFrame.from_records(
        users_list, columns=["username", "userUid"]
    )
    return device_dataframe.merge(users_dataframe, how="left", on="userUid")


@devices.command(
    name="list-backup-sets",
    help="Get information about many devices and their backup sets",
)
@active_option
@org_uid_option
@include_usernames_option
@format_option
@sdk_options()
def list_backup_sets(
    state, active, org_uid, include_usernames, format,
):
    """Outputs a list of all devices."""
    columns = ["guid", "userUid"]
    devices_dataframe = _get_device_dataframe(state.sdk, columns, active, org_uid)
    if include_usernames:
        devices_dataframe = _add_usernames_to_device_dataframe(
            state.sdk, devices_dataframe
        )
    devices_dataframe = _add_backup_set_settings_to_dataframe(
        state.sdk, devices_dataframe
    )
    formatter = DataFrameOutputFormatter(format)
    formatter.echo_formatted_dataframe(devices_dataframe)


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


@bulk.command(
    name="deactivate",
    help="""Deactivate all devices on the given list.
            Takes as input a CSV with a deviceId column.
            The deviceId column must have the legacy deviceId value, not GUID.""",
)
@read_csv_arg(headers=["deviceId"])
@change_device_name_option
@purge_date_option
@format_option
@sdk_options()
def bulk_deactivate(state, csv_rows, change_device_name, purge_date, format):
    sdk = state.sdk
    csv_rows[0]["deactivated"] = False
    formatter = OutputFormatter(format, {key: key for key in csv_rows[0].keys()})
    for row in csv_rows:
        row["change_device_name"] = change_device_name
        row["purge_date"] = purge_date

    def handle_row(**row):
        try:
            _deactivate_device(
                sdk, row["deviceId"], row["change_device_name"], row["purge_date"]
            )
            row["deactivated"] = "True"
        except Exception as e:
            row["deactivated"] = "False: {}".format(e)
        return row

    result_rows = run_bulk_process(
        handle_row, csv_rows, progress_label="Deactivating devices:"
    )
    formatter.echo_formatted_list(result_rows)
