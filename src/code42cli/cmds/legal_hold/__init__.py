from collections import OrderedDict
from functools import lru_cache
from pprint import pprint

from py42.exceptions import Py42ForbiddenError, Py42BadRequestError


from code42cli.errors import (
    UserAlreadyAddedError,
    UserNotInLegalHoldError,
    LegalHoldNotFoundOrPermissionDeniedError,
)
from code42cli.util import (
    format_to_table,
    find_format_width,
    format_string_list_to_columns,
    get_user_id,
)
from code42cli.bulk import run_bulk_process
from code42cli.file_readers import create_csv_reader
from code42cli.logger import get_main_cli_logger

_MATTER_KEYS_MAP = OrderedDict()
_MATTER_KEYS_MAP[u"legalHoldUid"] = u"Matter ID"
_MATTER_KEYS_MAP[u"name"] = u"Name"
_MATTER_KEYS_MAP[u"description"] = u"Description"
_MATTER_KEYS_MAP[u"creator_username"] = u"Creator"
_MATTER_KEYS_MAP[u"creationDate"] = u"Creation Date"

logger = get_main_cli_logger()


def add_user(sdk, matter_id, username):
    user_id = get_user_id(sdk, username)
    matter = _check_matter_is_accessible(sdk, matter_id)
    try:
        sdk.legalhold.add_to_matter(user_id, matter_id)
    except Py42BadRequestError as e:
        if u"USER_ALREADY_IN_HOLD" in e.response.text:
            matter_id_and_name_text = u"legal hold matter id={}, name={}".format(
                matter_id, matter[u"name"]
            )
            raise UserAlreadyAddedError(username, matter_id_and_name_text)
        raise


def remove_user(sdk, matter_id, username):
    _check_matter_is_accessible(sdk, matter_id)
    membership_id = _get_legal_hold_membership_id_for_user_and_matter(sdk, username, matter_id)
    sdk.legalhold.remove_from_matter(membership_id)


def get_matters(sdk):
    matters = _get_all_active_matters(sdk)
    if matters:
        rows, column_size = find_format_width(matters, _MATTER_KEYS_MAP)
        format_to_table(rows, column_size)


def add_bulk_users(sdk, file_name):
    reader = create_csv_reader(file_name)
    run_bulk_process(
        lambda matter_id, username: add_user(sdk, matter_id, username), reader,
    )


def remove_bulk_users(sdk, file_name):
    reader = create_csv_reader(file_name)
    run_bulk_process(
        lambda matter_id, username: remove_user(sdk, matter_id, username), reader,
    )


def show_matter(sdk, matter_id, include_inactive=False, include_policy=False):
    matter = _check_matter_is_accessible(sdk, matter_id)
    matter[u"creator_username"] = matter[u"creator"][u"username"]

    # if `active` is None then all matters (whether active or inactive) are returned. True returns
    # only those that are active.
    active = None if include_inactive else True
    memberships = _get_legal_hold_memberships_for_matter(sdk, matter_id, active=active)
    active_usernames = [member[u"user"][u"username"] for member in memberships if member[u"active"]]
    inactive_usernames = [
        member[u"user"][u"username"] for member in memberships if not member[u"active"]
    ]

    rows, column_size = find_format_width([matter], _MATTER_KEYS_MAP)

    print(u"")
    format_to_table(rows, column_size)
    if active_usernames:
        print(u"\nActive matter members:\n")
        format_string_list_to_columns(active_usernames)
    else:
        print("\nNo active matter members.\n")

    if include_inactive:
        if inactive_usernames:
            print(u"\nInactive matter members:\n")
            format_string_list_to_columns(inactive_usernames)
        else:
            print("No inactive matter members.\n")

    if include_policy:
        _get_and_print_preservation_policy(sdk, matter[u"holdPolicyUid"])
        print(u"")


def _get_and_print_preservation_policy(sdk, policy_uid):
    preservation_policy = sdk.legalhold.get_policy_by_uid(policy_uid)
    print(u"\nPreservation Policy:\n")
    pprint(preservation_policy._data_root)


def _get_legal_hold_membership_id_for_user_and_matter(sdk, username, matter_id):
    user_id = get_user_id(sdk, username)
    memberships = _get_legal_hold_memberships_for_matter(sdk, matter_id, active=True)
    for member in memberships:
        if member[u"user"][u"userUid"] == user_id:
            return member[u"legalHoldMembershipUid"]
    raise UserNotInLegalHoldError(username, matter_id)


def _get_legal_hold_memberships_for_matter(sdk, matter_id, active=True):
    memberships_generator = sdk.legalhold.get_all_matter_custodians(
        legal_hold_uid=matter_id, active=active
    )
    memberships = [
        member for page in memberships_generator for member in page[u"legalHoldMemberships"]
    ]
    return memberships


def _get_all_active_matters(sdk):
    matters_generator = sdk.legalhold.get_all_matters()
    matters = [
        matter for page in matters_generator for matter in page[u"legalHolds"] if matter[u"active"]
    ]
    for matter in matters:
        matter[u"creator_username"] = matter[u"creator"][u"username"]
    return matters


@lru_cache(maxsize=None)
def _check_matter_is_accessible(sdk, matter_id):
    try:
        matter = sdk.legalhold.get_matter_by_uid(matter_id)
        return matter
    except (Py42BadRequestError, Py42ForbiddenError):
        raise LegalHoldNotFoundOrPermissionDeniedError(matter_id)
