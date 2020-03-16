from argparse import RawDescriptionHelpFormatter

from code42cli.securitydata.subcommands import clear_checkpoint, print_out, write_to
from code42cli.securitydata.subcommands import send_to


def init_subcommand(subcommand_parser):
    description = u"""
    Subcommands:
          print             - print details of a profile
          write-to          - create or update profile settings
          send-to           - change stored password
          clear-checkpoint  - show all existing stored profiles
    """
    securitydata_arg_parser = subcommand_parser.add_parser(
        u"securitydata", formatter_class=RawDescriptionHelpFormatter, description=description
    )
    securitydata_subparsers = securitydata_arg_parser.add_subparsers(title=u"subcommands")
    send_to.init(securitydata_subparsers)
    write_to.init(securitydata_subparsers)
    print_out.init(securitydata_subparsers)
    clear_checkpoint.init(securitydata_subparsers)
