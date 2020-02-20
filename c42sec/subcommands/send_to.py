from c42sec._internal.logger_factory import get_logger_for_server
from c42sec._internal.arguments import add_all_arguments_to_parser
from c42sec._internal.extraction import extract
from c42sec._internal.options import ServerProtocol


def init(subcommand_parser):
    parser = subcommand_parser.add_parser("send-to")
    parser.set_defaults(func=send_to)
    _add_server_arg(parser)
    _add_protocol_arg(parser)
    add_all_arguments_to_parser(parser)


def send_to(args):
    logger = get_logger_for_server(args.server, args.protocol, args.format)
    extract(logger, args)


def _add_server_arg(parser):
    parser.add_argument(action="store", dest="server", help="The server address to send output to.")


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
