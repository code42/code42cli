from collections import OrderedDict
from datetime import date

import click
from pandas import DataFrame
from py42 import exceptions

from code42cli.click_ext.groups import OrderedGroup
from code42cli.errors import Code42CLIError
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.file_readers import read_csv_arg
from code42cli.bulk import run_bulk_process
from code42cli.output_formats import OutputFormatter


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def devices(state):
    """For managing computers within Code42."""
    pass


device_id_option = click.option(
    "--device-id",
    required=True,
    type=str,
    help="The device ID for the device on which you wish to act.",
)

change_device_name_option = click.option(
    "--change-device-name",
    required=False,
    is_flag=True,
    default=False,
    help='Include to prepend "deactivated_" and today\'s date to the name of any deactivated devices.',
)

purge_date_option = click.option(
    "--purge-date",
    required=False,
    type=str,
    default=None,
    help="The date on which the archive should be purged from cold storage in yyyy-MM-dd format. If not provided, the date will be set according to the appropriate org settings.",
)


@devices.command()
@device_id_option
@change_device_name_option
@purge_date_option
@sdk_options()
def deactivate(state, device_id, change_device_name, purge_date):
    """Deactivate a device within Code42"""
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


_DEVICE_INFO_KEYS_MAP = OrderedDict()
_DEVICE_INFO_KEYS_MAP["computerId"] = "Device ID"
_DEVICE_INFO_KEYS_MAP["name"] = "Name"
_DEVICE_INFO_KEYS_MAP["osHostname"] = "Hostname"
_DEVICE_INFO_KEYS_MAP["guid"] = "GUID"
_DEVICE_INFO_KEYS_MAP["status"] = "Status"
_DEVICE_INFO_KEYS_MAP["archiveBytes"] = "Largest Archive Size in Bytes"
_DEVICE_INFO_KEYS_MAP["lastConnected"] = "Last Connected Date"
_DEVICE_INFO_KEYS_MAP["lastBackup"] = "Last Backup Date"
_DEVICE_INFO_KEYS_MAP["lastCompletedBackup"] = "Last Completed Backup Date"
_DEVICE_INFO_KEYS_MAP["productVersion"] = "Code42 Version"
_DEVICE_INFO_KEYS_MAP["osName"] = "Operating System"
_DEVICE_INFO_KEYS_MAP["osVersion"] = "Operating System Version"


@devices.command()
@device_id_option
@format_option
@sdk_options()
def get_info(state, device_id, format=None):
    """Print device info."""
    formatter = OutputFormatter(format, _DEVICE_INFO_KEYS_MAP)
    device_info = _get_device_info(state.sdk, device_id)
    if device_info:
        formatter.echo_formatted_list([device_info])


def _get_device_info(sdk, device_id):
    device = sdk.devices.get_by_id(device_id, include_backup_usage=True).data
    device["archiveBytes"] = (
        max(
            [
                backupDestination["archiveBytes"]
                for backupDestination in device["backupUsage"]
            ]
        )
        if len(device["backupUsage"]) > 0
        else 0
    )
    device["lastBackup"] = (
        max(
            [
                backupDestination["lastBackup"]
                for backupDestination in device["backupUsage"]
            ]
        )
        if len(device["backupUsage"]) > 0
        else None
    )
    device["lastCompletedBackup"] = (
        max(
            [
                backupDestination["lastCompletedBackup"]
                for backupDestination in device["backupUsage"]
            ]
        )
        if len(device["backupUsage"]) > 0
        else None
    )
    return device


@devices.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def bulk(state):
    """Tools for managing devices in bulk"""
    pass


@bulk.command(name="info", help="Get information about many devices")
@click.option(
    '--active',
    required=False,
    type=bool,
    default=None,
    help='Include to return only active devices.'
)
@click.option(
    '--org-uid',
    required=False,
    type=str,
    default=None,
    help="Optionally provide to limit devices to only the ones in the org you specify. Note that child orgs will be included."
)
@click.option(
    '--drop-most-recent',
    required=False,
    type=int,
    help="Will drop the X most recently connected devices for each user from the result list where X is the number you provide as this argument. Can be used to avoid passing the most recently connected device for a user to the deactivate command"
)
@click.option(
    '--include-backup-usage',
    required=False,
    type=bool,
    default=False,
    help='Include to return backup usage information for each device (may significantly lengthen the size of the return)'
)
@sdk_options()
def bulk_list(state, active, drop_most_recent, org_uid, include_backup_usage):
    """Outputs a list of all devices in the tenant"""
    devices_dataframe = _get_device_dataframe(state.sdk, active, org_uid, include_backup_usage)
    if drop_most_recent:
        devices_dataframe = _drop_n_devices_per_user(devices_dataframe, drop_most_recent)
    click.echo(devices_dataframe.to_csv())

def _get_device_dataframe(sdk, active=None, org_uid=None, include_backup_usage=False):
    devices_generator = sdk.devices.get_all(active=active, include_backup_usage=include_backup_usage, org_uid=org_uid)
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
            "userUid"
        ],
    )

def _drop_n_devices_per_user(device_dataframe,number_to_drop,sort_field='lastConnected',sort_ascending=False,group_field='userUid'):
    return device_dataframe.sort_values(by=sort_field, ascending=sort_ascending).drop(
        device_dataframe.groupby(group_field).head(number_to_drop).index
    ).reset_index(drop=True)

@bulk.command(name='deactivate', help="Deactivate all devices on the given list. Takes as input a CSV with a deviceId column")
@read_csv_arg(headers=["deviceId"])
@change_device_name_option
@purge_date_option
@sdk_options()
def bulk_deactivate(state, csv_rows, change_device_name, purge_date):
    sdk = state.sdk
    for row in csv_rows:
        row["change_device_name"] = change_device_name
        row["purge_date"] = purge_date
    click.echo(csv_rows)
    def handle_row(deviceId, change_device_name, purge_date):
        _deactivate_device(sdk, deviceId, change_device_name, purge_date)

    run_bulk_process(
        handle_row, csv_rows, progress_label="Deactivating devices:"
    )