from code42cli.securitydata.subcommands import clear_checkpoint, print_out, write_to
from code42cli.securitydata.subcommands import send_to


def init_subcommand(subcommand_parser):
    securitydata_arg_parser = subcommand_parser.add_parser("securitydata")
    securitydata_subparser = securitydata_arg_parser.add_subparsers()
    send_to.init(securitydata_subparser)
    write_to.init(securitydata_subparser)
    print_out.init(securitydata_subparser)
    clear_checkpoint.init(securitydata_subparser)
