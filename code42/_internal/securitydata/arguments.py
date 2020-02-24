from code42._internal.securitydata.options import ExposureType, OutputFormat


def add_all_arguments_to_parser(parser):
    _add_advanced_query(parser)
    _add_begin_date_arg(parser)
    _add_end_date_arg(parser)
    _add_output_format_arg(parser)
    _add_incremental_arg(parser)
    _add_exposure_types_arg(parser)
    _add_debug_args(parser)


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
        default=OutputFormat.JSON,
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


def _add_exposure_types_arg(parser):
    parser.add_argument(
        "-t",
        "--types",
        nargs="*",
        action="store",
        dest="exposure_types",
        choices=list(ExposureType()),
        help="To limit extracted events to those with given exposure types.",
    )


def _add_debug_args(parser):
    parser.add_argument(
        "-d", "--debug", dest="is_debug_mode", action="store_true", help="Turn on Debug logging."
    )
