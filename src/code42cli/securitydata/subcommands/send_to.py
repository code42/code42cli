import code42cli.arguments as main_args
from code42cli.securitydata.arguments import main as securitydata_main_args
from code42cli.securitydata.arguments import search as search_args
from code42cli.securitydata.extraction import extract
from code42cli.securitydata.logger_factory import get_logger_for_server
from code42cli.securitydata.options import ServerProtocol


def init(subcommand_parser):
    """Sets up the `send-to` subcommand for sending logs to a server, such as SysLog.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser
    """
    parser = subcommand_parser.add_parser("send-to")
    parser.set_defaults(func=send_to)
    _add_server_arg(parser)
    _add_protocol_arg(parser)
    search_args.add_arguments_to_parser(parser)
    securitydata_main_args.add_arguments_to_parser(parser)
    main_args.add_arguments_to_parser(parser)


def send_to(args):
    """Activates 'send-to' command. It gets security events and logs them to the given server."""
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
        choices=ServerProtocol(),
        default=ServerProtocol.UDP,
        help="Protocol used to send logs to server.",
    )
