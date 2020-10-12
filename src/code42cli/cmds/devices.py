import click
from click import echo

from code42cli.bulk import generate_template_cmd_factory
from code42cli.bulk import run_bulk_process
from code42cli.click_ext.groups import OrderedGroup
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import OutputFormatter
from code42cli.util import format_string_list_to_columns
from code42cli.errors import Code42CLIError

from py42 import exceptions


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def devices(state):
	"""For managing computers within Code42."""
	pass

device_id_option = click.option(
	'--device-id',
	required=True,
	type=str,
	help='The device ID for the device on which you wish to act.'
)

@devices.command()
@device_id_option
@sdk_options()
def deactivate(state,device_id):
	"""Deactivate a device within Code42"""
	_deactivate_device(state.sdk, device_id)

def _deactivate_device(sdk, device_id):
	try:
		sdk.devices.deactivate(device_id)
	except exceptions.Py42BadRequestError:
		raise Code42CLIError(u"The device {} is in legal hold.".format(device_id))
	except exceptions.Py42NotFoundError:
		raise Code42CLIError(u"The device {} was not found.".format(device_id))
	except exceptions.Py42ForbiddenError:
		raise Code42CLIError(u"Unable to deactivate {}.".format(device_id))
