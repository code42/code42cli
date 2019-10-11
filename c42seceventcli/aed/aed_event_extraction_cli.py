from argparse import ArgumentParser
from keyring import get_credential, get_password, set_password, delete_password
from getpass import getpass
import urllib3


from py42.sdk import SDK
from py42 import settings
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers

from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cli_args import (
    get_required_args,
    add_username_arg,
    add_begin_timestamp_arg,
    add_help_arg,
    add_ignore_ssl_errors_arg,
)

_SERVICE = "c42seceventcli"


def main():
    parser = _get_arg_parser()
    args = parser.parse_args()

    if args.c42_ignore_ssl_errors:
        _ignore_ssl_errors()

    username = args.c42_username
    password = _get_password(username)

    sdk = _create_sdk(
        address=args.c42_authority_url,
        username=username,
        password=password
    )

    handlers = _create_handlers()
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract()


def _get_arg_parser():
    parser = ArgumentParser(add_help=False)
    required_group = get_required_args(parser)
    add_username_arg(required_group)

    required_group.add_argument(
        "-o", "--output-format",
        dest="c42_output_format",
        action="store",
        help="Either CEF or JSON"
    )

    optional = parser.add_argument_group("optional arguments")
    add_help_arg(optional)
    add_begin_timestamp_arg(optional)
    add_ignore_ssl_errors_arg(optional)
    return parser


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_password(username):
    password = get_password(_SERVICE, username)
    if password is None:
        password = getpass()
        set_password(_SERVICE, username, password)

    return password


def _create_sdk(address, username, password):
    return SDK.create_using_local_account(
        host_address=address, username=username, password=password
    )


def _create_handlers():
    store = AEDCursorStore()
    handlers = FileEventHandlers()

    handlers.record_cursor_position = store.replace_stored_insertion_timestamp
    handlers.get_cursor_position = store.get_stored_insertion_timestamp
    handlers.handle_response = _handle_response
    return handlers


def _handle_response(response):
    print(response.text)
    # TODO: Replace with logging


if __name__ == "__main__":
    main()
