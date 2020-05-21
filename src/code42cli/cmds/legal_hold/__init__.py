from collections import OrderedDict

from py42.exceptions import Py42Error
from py42.util import format_json

from code42cli.errors import UserAlreadyAddedError
from code42cli.util import format_to_table, find_format_width
from code42cli.bulk import run_bulk_process, CSVReader
from code42cli.logger import get_main_cli_logger
from code42cli.cmds.detectionlists import get_user_id


_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP[u"legalHoldUid"] = u"Matter ID"
_HEADER_KEYS_MAP[u"name"] = u"Name"
_HEADER_KEYS_MAP[u"description"] = u"Description"
_HEADER_KEYS_MAP[u"creator_username"] = u"Creator"


def add_user(sdk, matter_id, username):
    user_id = get_user_id(sdk, username)
    try:
        sdk.legalhold.add_to_matter(user_id, matter_id)
    except Py42Error as e:
        error_text = e.response.text
        if u"USER_ALREADY_IN_HOLD" in error_text:
            matter_text = u"legal hold matter {}".format(matter_id)
            raise UserAlreadyAddedError(username, matter_text)
        else:
            get_main_cli_logger().print_and_log_error(error_text)


def remove_user(sdk, matter_id, username):
    user_id = get_user_id(sdk, username)
    try:
        membership_id = _get_legal_hold_membership_id_for_user_and_matter(sdk, user_id, matter_id)
        sdk.legalhold.remove_from_matter(membership_id)
    except Py42Error as e:
        error_text = e.response.text
        get_main_cli_logger().print_and_log_error(error_text)


def _get_legal_hold_membership_id_for_user_and_matter(sdk, user_id, matter_id):
    memberships_generator = sdk.legalhold.get_all_matter_custodians(
        legal_hold_uid=matter_id, active=True
    )
    for page in memberships_generator:
        for membership in page[u"legalHoldMemberships"]:
            if membership[u"user"][u"userUid"] == user_id:
                return membership[u"legalHoldMembershipUid"]
    raise UserNotInHoldError(username, matter_id)


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
    matter = sdk.legalhold.get_matter_by_uid(matter_id)
    policy_uid = matter[u"holdPolicyUid"]
    preservation_policy = sdk.legalhold.get_policy_by_uid(policy_uid)
    members_generator = sdk.legalhold.get_all_matter_custodians(legal_hold_uid=matter_id)
    members_list = [
        member
        for page in members_generator
        for member in page[u"legalHoldMemberships"]
        if member[u"active"]
    ]
    from pprint import pprint

    print("Matter:\n")
    pprint(matter._data_root)
    print("\nPreservation Policy:\n")
    pprint(preservation_policy._data_root)
    print("\nMatter members:\n")
    pprint(members_list)
