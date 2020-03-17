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
    parser = subcommand_parser.add_parser(
        u"send-to",
        description=u"Send file events to the given server address.",
        usage=u"code42 securitydata send-to <server-address> <optional-args>",
    )
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
    parser.add_argument(
        action=u"store", dest=u"server", help=u"The server address to send output to."
    )


def _add_protocol_arg(parser):
    parser.add_argument(
        u"-p",
        u"--protocol",
        action=u"store",
        dest=u"protocol",
        choices=ServerProtocol(),
        default=ServerProtocol.UDP,
        help=u"Protocol used to send logs to server.",
    )
