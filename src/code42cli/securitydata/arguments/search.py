from code42cli.securitydata.options import ExposureType


def add_arguments_to_parser(parser):
    _add_advanced_query(parser)
    _add_begin_date_arg(parser)
    _add_end_date_arg(parser)
    _add_exposure_types_arg(parser)


class SearchArguments(object):
    ADVANCED_QUERY = "advanced_query"
    BEGIN_DATE = "begin_date"
    END_DATE = "end_date"
    EXPOSURE_TYPES = "exposure_types"

    def __iter__(self):
        return iter([self.ADVANCED_QUERY, self.BEGIN_DATE, self.END_DATE, self.EXPOSURE_TYPES])


def _add_advanced_query(parser):
    parser.add_argument(
        "--advanced-query",
        action="store",
        dest=SearchArguments.ADVANCED_QUERY,
        help="A raw JSON file event query. "
        "Useful for when the provided query parameters do not satisfy your requirements."
        "WARNING: Using advanced queries ignores all other query parameters.",
    )


def _add_begin_date_arg(parser):
    parser.add_argument(
        "-b",
        "--begin",
        action="store",
        dest=SearchArguments.BEGIN_DATE,
        help="The beginning of the date range in which to look for events, "
        "in YYYY-MM-DD UTC format OR a number (number of minutes ago).",
    )


def _add_end_date_arg(parser):
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        dest=SearchArguments.END_DATE,
        help="The end of the date range in which to look for events, "
        "in YYYY-MM-DD UTC format OR a number (number of minutes ago).",
    )


def _add_exposure_types_arg(parser):
    parser.add_argument(
        "-t",
        "--types",
        nargs="*",
        action="store",
        dest=SearchArguments.EXPOSURE_TYPES,
        choices=ExposureType(),
        metavar=tuple(ExposureType()),
        help="Limits extracted events to those with given exposure types.",
    )
