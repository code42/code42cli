from collections import OrderedDict

from py42.exceptions import Py42InternalServerError
from py42.util import format_json

from code42cli.util import format_to_table, find_format_width
from code42cli.bulk import run_bulk_process, CSVReader
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.detectionlists import get_user_id


_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP[u"legalHoldUid"] = u"Matter ID"
_HEADER_KEYS_MAP[u"name"] = u"Name"
_HEADER_KEYS_MAP[u"description"] = u"Description"
_HEADER_KEYS_MAP[u"creator_username"] = u"Creator"


def add_user(sdk, profile, matter_id, username):
    pass


def remove_user(sdk, profile, matter_id, username):
    pass


def _get_all_active_matters(sdk):
    matters_generator = sdk.legalhold.get_all_matters()
    matters = [
        matter for page in matters_generator for matter in page[u"legalHolds"] if matter[u"active"]
    ]
    for matter in matters:
        matter[u"creator_username"] = matter[u"creator"][u"username"]
    return matters


def get_matters(sdk):
    matters = _get_all_active_matters(sdk)
    if matters:
        rows, column_size = find_format_width(matters, _HEADER_KEYS_MAP)
        format_to_table(rows, column_size)


def add_bulk_users(sdk, profile, file_name):
    run_bulk_process(
        file_name,
        lambda matter_id, username: add_user(sdk, profile, matter_id, username),
        CSVReader(),
    )


def remove_bulk_users(sdk, profile, file_name):
    run_bulk_process(
        file_name,
        lambda matter_id, username: remove_user(sdk, profile, matter_id, username),
        CSVReader(),
    )


def show_matter(sdk, matter_id):
    pass
