from argparse import RawDescriptionHelpFormatter

from code42cli.securitydata.subcommands import clear_checkpoint, print_out, write_to
from code42cli.securitydata.subcommands import send_to


def init_subcommand(subcommand_parser):
    description = u"""
    Subcommands:
            print             - Prints file events to stdout.
            send-to           - Sends file events to the given server address.
            write-to          - Writes file events to the file with the given name.
            clear-checkpoint  - Removes the saved checkpoint from "incremental" mode.
    """
    securitydata_arg_parser = subcommand_parser.add_parser(
        u"securitydata",
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        epilog=u"Use --profile to do any of these commands for the given profile.",
    )
    securitydata_subparsers = securitydata_arg_parser.add_subparsers(title=u"subcommands")
    send_to.init(securitydata_subparsers)
    write_to.init(securitydata_subparsers)
    print_out.init(securitydata_subparsers)
    clear_checkpoint.init(securitydata_subparsers)
