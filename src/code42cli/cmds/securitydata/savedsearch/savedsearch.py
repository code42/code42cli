from pprint import pprint

from code42cli.util import format_to_table, find_format_width
from code42cli.cmds.search_shared import logger_factory
from code42cli.cmds.search_shared.enums import OutputFormat
from code42cli.cmds.securitydata.extraction import extract_saved_search


def show(sdk, profile):
    response = sdk.securitydata.savedsearches.get()
    header = {u"name": u"Name", u"id": u"Id"}
    return format_to_table(*find_format_width(response[u"searches"], header))


def show_detail(sdk, profile, search_id):
    response = sdk.securitydata.savedsearches.get_by_id(search_id)
    pprint(response["searches"])


def print_out(sdk, profile, search_id, incremental=True):
    """Activates 'print' command. It gets security events and prints them to stdout."""
    logger = logger_factory.get_logger_for_stdout(OutputFormat.RAW)
    query = sdk.securitydata.savedsearches.get_query(search_id)
    extract_saved_search(sdk, profile, logger, query, incremental=incremental)


def write_to(sdk, profile, search_id, filename, incremental=True):
    """Activates 'write-to' command. It gets security events and writes them to the given file."""
    logger = logger_factory.get_logger_for_file(filename, OutputFormat.RAW)
    query = sdk.securitydata.savedsearches.get_query(search_id)
    extract_saved_search(sdk, profile, logger, query, incremental=incremental)


def send_to(sdk, profile, search_id, server, protocol, incremental=True):
    """Activates 'send-to' command. It gets security events and logs them to the given server."""
    logger = logger_factory.get_logger_for_server(server, protocol, OutputFormat.RAW)
    query = sdk.securitydata.savedsearches.get_query(search_id)
    extract_saved_search(sdk, profile, logger, query, incremental=incremental)
