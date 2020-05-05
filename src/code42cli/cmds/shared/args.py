from code42cli.cmds.shared.enums import SearchArguments, OutputFormat
from code42cli.args import ArgConfig


def create_search_args(search_for, filter_args):
    search_args = {
        SearchArguments.ADVANCED_QUERY: ArgConfig(
            u"--{}".format(SearchArguments.ADVANCED_QUERY.replace(u"_", u"-")),
            metavar=u"QUERY_JSON",
            help=u"A raw JSON {0} query. "
            u"Useful for when the provided query parameters do not satisfy your requirements.\n"
            u"WARNING: Using advanced queries is incompatible with other .".format(search_for),
        ),
        SearchArguments.BEGIN_DATE: ArgConfig(
            u"-b",
            u"--{}".format(SearchArguments.BEGIN_DATE),
            metavar=u"DATE",
            help=u"The beginning of the date range in which to look for {0}, "
            u"can be a date/time in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.".format(search_for),
        ),
        SearchArguments.END_DATE: ArgConfig(
            u"-e",
            u"--{}".format(SearchArguments.END_DATE),
            metavar=u"DATE",
            help=u"The end of the date range in which to look for {0}, "
            u"can be a date/time in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.".format(search_for),
        ),
    }
    format_and_incremental_args = {
        u"format": ArgConfig(
            u"-f",
            u"--format",
            choices=OutputFormat(),
            default=OutputFormat.JSON,
            help=u"The format used for outputting {0}.".format(search_for),
        ),
        u"incremental": ArgConfig(
            u"-i",
            u"--incremental",
            action=u"store_true",
            help=u"Only get {0} that were not previously retrieved.".format(search_for),
        ),
    }
    search_args.update(filter_args)
    search_args.update(format_and_incremental_args)
    return search_args
