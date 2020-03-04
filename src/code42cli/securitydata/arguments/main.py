from code42cli.securitydata.options import OutputFormat


IS_INCREMENTAL_KEY = "is_incremental"


def add_arguments_to_parser(parser):
    _add_output_format_arg(parser)
    _add_incremental_arg(parser)
    _add_debug_arg(parser)


def _add_output_format_arg(parser):
    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        action="store",
        choices=OutputFormat(),
        default=OutputFormat.JSON,
        help="The format used for outputting events.",
    )


def _add_incremental_arg(parser):
    parser.add_argument(
        "-i",
        "--incremental",
        dest=IS_INCREMENTAL_KEY,
        action="store_true",
        help="Only get events that were not previously retrieved.",
    )


def _add_debug_arg(parser):
    parser.add_argument(
        "-d", "--debug", dest="is_debug_mode", action="store_true", help="Turn on Debug logging."
    )


def _add_silence_result_status_arg(parser):
    parser.add_argument(
        "--silence-result-status",
        dest="silence_result_status",
        action="store_true",
        help="Whether to silence the outcome status. "
        "This is useful when piping output into other commands.",
    )
