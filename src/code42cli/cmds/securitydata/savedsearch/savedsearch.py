from pprint import pprint

from code42cli.util import format_to_table, find_format_width


def show(sdk, profile):
    response = sdk.securitydata.savedsearches.get()
    header = {u"name": u"Name", u"id": u"Id"}
    return format_to_table(*find_format_width(response[u"searches"], header))


def show_detail(sdk, profile, search_id):
    response = sdk.securitydata.savedsearches.get_by_id(search_id)
    pprint(response["searches"])

