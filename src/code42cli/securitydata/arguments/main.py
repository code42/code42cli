from code42cli.securitydata.options import OutputFormat


IS_INCREMENTAL_KEY = u"is_incremental"


def add_arguments_to_parser(parser):
    _add_output_format_arg(parser)
    _add_incremental_arg(parser)


def _add_output_format_arg(parser):
    parser.add_argument(
        u"-f",
        u"--format",
        dest=u"format",
        action=u"store",
        choices=OutputFormat(),
        default=OutputFormat.JSON,
        help=u"The format used for outputting events.",
    )


def _add_incremental_arg(parser):
    parser.add_argument(
        u"-i",
        u"--incremental",
        dest=IS_INCREMENTAL_KEY,
        action=u"store_true",
        help=u"Only get events that were not previously retrieved.",
    )
