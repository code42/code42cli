from collections import OrderedDict
from datetime import date

import click
from py42 import exceptions

from code42cli.click_ext.groups import OrderedGroup
from code42cli.errors import Code42CLIError
from code42cli.options import format_option
from code42cli.options import sdk_options
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
_DEVICE_INFO_KEYS_MAP["name"] = "Name"
_DEVICE_INFO_KEYS_MAP["osHostname"] = "Hostname"
_DEVICE_INFO_KEYS_MAP["guid"] = "GUID"
_DEVICE_INFO_KEYS_MAP["status"] = "Status"
_DEVICE_INFO_KEYS_MAP["archiveBytes"] = "Largest Archive Size in Bytes"
_DEVICE_INFO_KEYS_MAP["lastConnected"] = "Last Connected Date"
_DEVICE_INFO_KEYS_MAP["lastBackup"] = "Last Sent Backup Data Date"
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
    device["archiveBytes"] = max(
        [
            backupDestination["archiveBytes"]
            for backupDestination in device["backupUsage"]
        ]
    )
    device["lastBackup"] = max(
        [backupDestination["lastBackup"] for backupDestination in device["backupUsage"]]
    )
    device["lastCompletedBackup"] = max(
        [
            backupDestination["lastCompletedBackup"]
            for backupDestination in device["backupUsage"]
        ]
    )
    return device
