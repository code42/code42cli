class OutputFormat(object):
    CEF = "CEF"
    JSON = "JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON])


def add_args(parser):
    _add_begin_date_arg(parser)
    _add_end_date_arg(parser)
    _add_incremental_arg(parser)
    _add_output_format_arg(parser)
    _add_advanced_query(parser)


def _add_advanced_query(parser):
    parser.add_argument(
        "--advanced-query",
        action="store",
        dest="advanced_query",
        help="A raw JSON file event query. "
        "Useful for when the provided query parameters do not satisfy your requirements."
        "WARNING: Using advanced queries ignores all other query parameters.",
    )


def _add_begin_date_arg(parser):
    parser.add_argument(
        "-b",
        "--begin",
        action="store",
        dest="begin_date",
        help="The beginning of the date range in which to look for events, "
        "in YYYY-MM-DD UTC format OR a number (number of minutes ago).",
    )


def _add_end_date_arg(parser):
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        dest="end_date",
        help="The end of the date range in which to look for events, "
        "in YYYY-MM-DD UTC format OR a number (number of minutes ago).",
    )


def _add_output_format_arg(parser):
    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        action="store",
        choices=list(OutputFormat()),
        help="The format used for outputting events.",
    )


def _add_incremental_arg(parser):
    parser.add_argument(
        "-i",
        "--incremental",
        dest="is_incremental",
        action="store_true",
        help="Only get events that were not previously retrieved.",
    )
