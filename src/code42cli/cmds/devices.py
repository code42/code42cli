from collections import OrderedDict
from datetime import date
from datetime import datetime

import click
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
from code42cli.output_formats import OutputFormatter


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def devices(state):
    """For managing devices within your Code42 environment."""
    pass


device_id_argument = click.argument("device-id", type=str)

change_device_name_option = click.option(
    "--change-device-name",
    required=False,
    is_flag=True,
    default=False,
    help="""Include to prepend "deactivated_" and today's date to the name of any
    deactivated devices.""",
)

purge_date_option = click.option(
    "--purge-date",
    required=False,
    type=str,
    default=None,
    help="""The date on which the archive should be purged from cold storage in yyyy-MM-dd format.
    If not provided, the date will be set according to the appropriate org settings.""",
)


@devices.command()
@device_id_argument
@change_device_name_option
@purge_date_option
@sdk_options()
def deactivate(state, device_id, change_device_name, purge_date):
    """Deactivate a device within Code42. Requires the device ID to deactivate."""
    _deactivate_device(state.sdk, device_id, change_device_name, purge_date)


def _deactivate_device(sdk, device_id, change_device_name, purge_date):
    try:
        sdk.devices.deactivate(device_id)
    except exceptions.Py42BadRequestError:
        raise Code42CLIError("The device {} is in legal hold.".format(device_id))
    except exceptions.Py42NotFoundError:
        raise Code42CLIError("The device {} was not found.".format(device_id))
    except exceptions.Py42ForbiddenError:
        raise Code42CLIError("Unable to deactivate {}.".format(device_id))
    if purge_date or change_device_name:
        device = sdk.devices.get_by_id(device_id)
        guid = device.data["guid"]
        name = device.data["name"]
    if purge_date:
        _update_cold_storage_purge_date(sdk, guid, purge_date)
    if change_device_name and not name.startswith("deactivated_"):
        _change_device_name(
            sdk, guid, "deactivated_" + date.today().strftime("%Y-%m-%d") + "_" + name
        )


def _update_cold_storage_purge_date(sdk, guid, purge_date):
    archives_response = sdk.archive.get_all_by_device_guid(guid)
    archive_guid_list = [
        archive["archiveGuid"]
        for page in archives_response
        for archive in page["archives"]
    ]
    for archive_guid in archive_guid_list:
        sdk.archive.update_cold_storage_purge_date(archive_guid, purge_date)


def _change_device_name(sdk, guid, name):
    device_settings = sdk.devices.get_settings(guid)
    device_settings.name = name
    sdk.devices.update_settings(device_settings)


@devices.command()
@device_id_argument
@format_option
@sdk_options()
def show(state, device_id, format=None):
    """Print device info."""
    _DEVICE_INFO_KEYS_MAP = OrderedDict()
    _DEVICE_INFO_KEYS_MAP["computerId"] = "Device ID"
    _DEVICE_INFO_KEYS_MAP["name"] = "Name"
    _DEVICE_INFO_KEYS_MAP["osHostname"] = "Hostname"
    _DEVICE_INFO_KEYS_MAP["guid"] = "GUID"
    _DEVICE_INFO_KEYS_MAP["status"] = "Status"
    _DEVICE_INFO_KEYS_MAP["lastConnected"] = "Last Connected Date"
    _DEVICE_INFO_KEYS_MAP["lastBackup"] = "Last Backup Activity Date"
    _DEVICE_INFO_KEYS_MAP["lastCompleted"] = "Last Completed Backup Date"
    _DEVICE_INFO_KEYS_MAP["archiveBytes"] = "Archive Size in Bytes"
    _DEVICE_INFO_KEYS_MAP["productVersion"] = "Code42 Version"
    _DEVICE_INFO_KEYS_MAP["osName"] = "Operating System"
    _DEVICE_INFO_KEYS_MAP["osVersion"] = "Operating System Version"
    formatter = OutputFormatter(format, _DEVICE_INFO_KEYS_MAP)
    device_info = _get_device_info(state.sdk, device_id)
    formatter.echo_formatted_list([device_info])


def _get_device_info(sdk, device_id):
    device = sdk.devices.get_by_id(device_id, include_backup_usage=True).data
    if len(device["backupUsage"]) == 0:
        device["archiveBytes"] = 0
        device["lastBackup"] = None
        device["lastCompletedBackup"] = None
    else:
        device["lastBackup"] = _get_key_from_list_of_dicts(
            "lastBackup", device["backupUsage"]
        )
        device["lastCompletedBackup"] = _get_key_from_list_of_dicts(
            "lastCompletedBackup", device["backupUsage"]
        )
        device["archiveBytes"] = _get_key_from_list_of_dicts(
            "archiveBytes", device["backupUsage"]
        )
    return device


def _get_key_from_list_of_dicts(key, list_of_dicts):
    return [item[key] for item in list_of_dicts]


@devices.command(name="list", help="Get information about many devices")
@click.option(
    "--active",
    required=False,
    type=bool,
    is_flag=True,
    default=None,
    help="Include to get only active or deactivated devices. Defaults to getting all devices.",
)
@click.option(
    "--days-since-last-connected",
    required=False,
    type=int,
    help="Return only devices that have not connected in the number of days specified.",
)
@click.option(
    "--org-uid",
    required=False,
    type=str,
    default=None,
    help="""Optionally provide to limit devices to only the ones in the org you specify.
    Note that child orgs will be included.""",
)
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
    help="""Include to return backup usage information for each device
    (may significantly lengthen the size of the return).""",
)
@click.option(
    "--include-usernames",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Include to add the username associated with a device to the output.",
)
@click.option(
    "--include-settings",
    required=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Include to include device settings in output.",
)
@sdk_options()
def list(
    state,
    active,
    days_since_last_connected,
    drop_most_recent,
    org_uid,
    include_backup_usage,
    include_usernames,
    include_settings,
):
    """Outputs a list of all devices."""
    devices_dataframe = _get_device_dataframe(
        state.sdk, active, org_uid, include_backup_usage
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
    click.echo_via_pager(devices_dataframe.to_csv())


def _get_device_dataframe(sdk, active=None, org_uid=None, include_backup_usage=False):
    devices_generator = sdk.devices.get_all(
        active=active, include_backup_usage=include_backup_usage, org_uid=org_uid
    )
    devices_list = []
    for page in devices_generator:
        devices_list.extend(page["computers"])
    return DataFrame.from_records(
        devices_list,
        columns=[
            "computerId",
            "guid",
            "name",
            "osHostname",
            "status",
            "lastConnected",
            "backupUsage",
            "productVersion",
            "osName",
            "osVersion",
            "userUid",
        ],
    )


def _add_settings_to_dataframe(sdk, device_dataframe):
    macos_guids = device_dataframe.loc[
        device_dataframe["osName"] == "mac", "guid"
    ].values
    rows = [
        {"guid": guid, "macos_guid": guid in macos_guids}
        for guid in device_dataframe["guid"].values
    ]

    def handle_row(guid, macos_guid):
        try:
            current_device_settings = sdk.devices.get_settings(guid)
        except Exception as e:
            return {
                "guid": guid,
                "ERROR": "Unable to retrieve device settings for {}: {}".format(
                    guid, e
                ),
            }
        current_result_dict = {
            "guid": current_device_settings.guid,
            "included_files": [
                backup_set.included_files
                for backup_set in current_device_settings.backup_sets
            ],
            "excluded_files": [
                backup_set.excluded_files
                for backup_set in current_device_settings.backup_sets
            ],
        }
        if macos_guid:
            try:
                full_disk_access_status = sdk.devices.get_agent_full_disk_access_state(
                    guid
                ).data[
                    "value"
                ]  # returns 404 error if device isn't a Mac or doesn't have full disk access
            except Py42NotFoundError:
                full_disk_access_status = False
        else:
            full_disk_access_status = ""
        current_result_dict["full_disk_access"] = full_disk_access_status
        return current_result_dict

    result_list = run_bulk_process(
        handle_row, rows, progress_label="Getting device settings"
    )
    try:
        return device_dataframe.merge(DataFrame.from_records(result_list), on="guid")
    except KeyError:
        return device_dataframe


def _drop_devices_which_have_not_connected_in_some_number_of_days(
    devices_dataframe, days_since_last_connected
):
    return devices_dataframe.loc[
        to_datetime(datetime.now(), utc=True)
        - to_datetime(devices_dataframe["lastConnected"], utc=True)
        > to_timedelta(days_since_last_connected, unit="days"),
        :,
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


@devices.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for managing devices in bulk."""
    pass


@bulk.command(
    name="deactivate",
    help="""Deactivate all devices on the given list.
            Takes as input a CSV with a deviceId column""",
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
