from argparse import RawDescriptionHelpFormatter

from code42cli.securitydata.subcommands import clear_checkpoint, print_out, write_to
from code42cli.securitydata.subcommands import send_to


def init_subcommand(subcommand_parser):
    description = u"""
    Subcommands:
            print             - Print file events to stdout.
            send-to           - Send file events to the given server address.
            write-to          - Write file events to the file with the given name.
            clear-checkpoint  - Remove the saved checkpoint from 'incremental' (-i) mode.
    """
    securitydata_arg_parser = subcommand_parser.add_parser(
        u"securitydata",
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        epilog=u"Use '--profile <profile-name>' to execute any of these commands for the given profile.",
        usage=u"code42 securitydata <subcommand> <optional args>",
    )
    securitydata_subparsers = securitydata_arg_parser.add_subparsers(title=u"subcommands")
    send_to.init(securitydata_subparsers)
    write_to.init(securitydata_subparsers)
    print_out.init(securitydata_subparsers)
    clear_checkpoint.init(securitydata_subparsers)
