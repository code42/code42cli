import c42sec._internal.query_args as query_args


def init(subcommand_parser):
    parser_for_write_command = subcommand_parser.add_parser("write-to")
    parser_for_write_command.set_defaults(func=write_to)
    _add_args_to_write_command(parser_for_write_command)


def write_to(args):
    print(args)


def _add_args_to_write_command(parser_for_write_command):
    query_args.add_begin_date_arg(parser_for_write_command)
    query_args.add_end_date_arg(parser_for_write_command)
    query_args.add_incremental_arg(parser_for_write_command)
    query_args.add_output_format_arg(parser_for_write_command)
    query_args.add_advanced_query(parser_for_write_command)
