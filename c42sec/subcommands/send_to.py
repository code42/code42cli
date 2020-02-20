from c42sec._internal.logger_factory import get_logger_for_syslog
from c42sec._internal.arguments import add_args
from c42sec._internal.extraction import extract_to_destination
from c42sec._internal.arg_options_enums import ServerProtocol


def init(subcommand_parser):
    parser = subcommand_parser.add_parser("send-to")
    parser.set_defaults(func=send_to)
    _add_server_arg(parser)
    _add_protocol_arg(parser)
    add_args(parser)


def send_to(args):
    logger = get_logger_for_syslog(args.server, args.protocol, args.format)
    extract_to_destination(logger, args)


def _add_server_arg(parser):
    parser.add_argument(
        "-s",
        "--server",
        action="store",
        dest="server",
        help="The server address to send output to.",
    )


def _add_protocol_arg(parser):
    parser.add_argument(
        "-p",
        "--protocol",
        action="store",
        dest="protocol",
        choices=list(ServerProtocol()),
        default=ServerProtocol.TCP,
        help="Protocol used to send logs to server. Ignored if destination type is not 'server'.",
    )
