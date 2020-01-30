from datetime import datetime, timedelta
from argparse import ArgumentParser

from c42sec.common.cli_args import (
    add_clear_cursor_arg,
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
import c42sec.common.util as common


def get_args():
    parser = _get_arg_parser()
    cli_args = vars(parser.parse_args())
    args = _union_cli_args_with_config_file_args(cli_args)
    args.cli_parser = parser
    args.initialize_args()
    args.verify_authority_arg()
    args.verify_username_arg()
    args.verify_destination_args()
    return args


def _get_arg_parser():
    parser = ArgumentParser()

    add_clear_cursor_arg(parser)
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


class AEDArgs(common.SecArgs):
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

    def initialize_args(self):
        self.destination_type = self.destination_type.lower()
        try:
            self.destination_port = int(self.destination_port)
        except ValueError:
            msg = "Destination port '{0}' not a base 10 integer.".format(self.destination_port)
            self._raise_value_error(msg)

    @staticmethod
    def _get_default_begin_date():
        default_begin_date = datetime.now() - timedelta(days=60)
        return default_begin_date.strftime("%Y-%m-%d")

    @staticmethod
    def _get_default_end_date():
        default_end_date = datetime.now()
        return default_end_date.strftime("%Y-%m-%d")

    def verify_authority_arg(self):
        if self.c42_authority_url is None:
            self._raise_value_error("Code42 authority host address not provided.")

    def verify_username_arg(self):
        if self.c42_username is None:
            self._raise_value_error("Code42 username not provided.")

    def verify_destination_args(self):
        self._verify_stdout_destination()
        self._verify_server_destination()

    def _verify_stdout_destination(self):
        if self.destination_type == "stdout" and self.destination is not None:
            msg = (
                "Destination '{0}' not applicable for stdout. "
                "Try removing '--dest' arg or change '--dest-type' to 'file' or 'server'."
            )
            msg = msg.format(self.destination)
            self._raise_value_error(msg)

    def _verify_file_destination(self):
        if self.destination_type == "file" and self.destination is None:
            msg = "Missing file name. Try: '--dest path/to/file'."
            self._raise_value_error(msg)

    def _verify_server_destination(self):
        if self.destination_type == "server" and self.destination is None:
            msg = "Missing server URL. Try: '--dest https://syslog.example.com'."
            self._raise_value_error(msg)

    def _raise_value_error(self, msg):
        self.cli_parser.print_usage()
        raise ValueError(msg)
