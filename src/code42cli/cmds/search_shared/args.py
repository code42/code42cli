from code42cli.cmds.search_shared.enums import SearchArguments, OutputFormat, AlertOutputFormat
from code42cli.args import ArgConfig


def create_search_args(search_for, filter_args):
    search_args = {
        SearchArguments.ADVANCED_QUERY: ArgConfig(
            u"--{}".format(SearchArguments.ADVANCED_QUERY.replace(u"_", u"-")),
            metavar=u"QUERY_JSON",
            help=u"A raw JSON {0} query. "
            u"Useful for when the provided query parameters do not satisfy your requirements.\n"
            u"WARNING: Using advanced queries is incompatible with other query-building args.".format(
                search_for
            ),
        ),
        SearchArguments.BEGIN_DATE: ArgConfig(
            u"-b",
            u"--{}".format(SearchArguments.BEGIN_DATE),
            metavar=u"DATE",
            help=u"The beginning of the date range in which to look for {1}, "
            u"can be a date/time in yyyy-MM-dd (UTC) or yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format "
            u"where the 'time' portion of the string can be partial (e.g. '2020-01-01 12' or '2020-01-01 01:15') "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.".format(u"beginning", search_for),
        ),
        SearchArguments.END_DATE: ArgConfig(
            u"-e",
            u"--{}".format(SearchArguments.END_DATE),
            metavar=u"DATE",
            help=u"The end of the date range in which to look for {0}, "
            u"argument format options are the same as --begin.".format(search_for),
        ),
    }
    format_enum = AlertOutputFormat() if search_for == "alerts" else OutputFormat()
    format_and_incremental_args = {
        u"format": ArgConfig(
            u"-f",
            u"--format",
            choices=format_enum,
            default=format_enum.JSON,
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
