from datetime import datetime, timedelta
from argparse import ArgumentParser

from c42seceventcli.common.cli_args import (
    add_clear_cursor_arg,
    add_reset_password_arg,
    add_config_file_path_arg,
    add_authority_host_address_arg,
    add_username_arg,
    add_begin_date_arg,
    add_end_date_arg,
    add_ignore_ssl_errors_arg,
    add_output_format_arg,
    add_record_cursor_arg,
    add_exposure_types_arg,
    add_debug_arg,
    add_destination_type_arg,
    add_destination_arg,
    add_destination_port_arg,
    add_destination_protocol_arg,
)
import c42seceventcli.common.common as common


def get_args():
    parser = _get_arg_parser()
    cli_args = vars(parser.parse_args())
    args = _union_cli_args_with_config_file_args(cli_args)
    args.cli_parser = parser
    return args


def _get_arg_parser():
    parser = ArgumentParser()

    add_clear_cursor_arg(parser)
    add_reset_password_arg(parser)
    add_config_file_path_arg(parser)
    add_authority_host_address_arg(parser)
    add_username_arg(parser)
    add_begin_date_arg(parser)
    add_ignore_ssl_errors_arg(parser)
    add_output_format_arg(parser)
    add_exposure_types_arg(parser)
    add_debug_arg(parser)
    add_destination_type_arg(parser)
    add_destination_arg(parser)
    add_destination_port_arg(parser)
    add_destination_protocol_arg(parser)

    # Makes sure that you can't give both an end_timestamp and record_cursor
    mutually_exclusive_timestamp_group = parser.add_mutually_exclusive_group()
    add_end_date_arg(mutually_exclusive_timestamp_group)
    add_record_cursor_arg(mutually_exclusive_timestamp_group)

    return parser


def _union_cli_args_with_config_file_args(cli_args):
    config_args = _get_config_args(cli_args.get("config_file"))
    args = AEDArgs()
    keys = cli_args.keys()
    for key in keys:
        args.try_set(key, cli_args.get(key), config_args.get(key))

    return args


def _get_config_args(config_file_path):
    try:
        return common.get_config_args(config_file_path)
    except IOError:
        print("Path to config file {0} not found".format(config_file_path))
        exit(1)


class AEDArgs(object):
    cli_parser = None
    c42_authority_url = None
    c42_username = None
    begin_date = None
    end_date = None
    ignore_ssl_errors = False
    output_format = "JSON"
    record_cursor = False
    exposure_types = None
    debug_mode = False
    destination_type = "stdout"
    destination = None
    destination_port = 514
    destination_protocol = "TCP"
    reset_password = False
    clear_cursor = False

    def __init__(self):
        self.begin_date = AEDArgs._get_default_begin_date()
        self.end_date = AEDArgs._get_default_end_date()

    def try_set(self, arg_name, cli_arg=None, config_arg=None):
        if cli_arg is not None:
            setattr(self, arg_name, cli_arg)
        elif config_arg is not None:
            setattr(self, arg_name, config_arg)

    @staticmethod
    def _get_default_begin_date():
        default_begin_date = datetime.now() - timedelta(days=60)
        return default_begin_date.strftime("%Y-%m-%d")

    @staticmethod
    def _get_default_end_date():
        default_end_date = datetime.now()
        return default_end_date.strftime("%Y-%m-%d")
