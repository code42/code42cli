from code42cli.securitydata.subcommands import clear_checkpoint, print_out, write_to
from code42cli.securitydata.subcommands import send_to


def init_subcommand(subcommand_parser):
    securitydata_arg_parser = subcommand_parser.add_parser(u"securitydata")
    securitydata_subparsers = securitydata_arg_parser.add_subparsers(title=u"subcommands")
    send_to.init(securitydata_subparsers)
    write_to.init(securitydata_subparsers)
    print_out.init(securitydata_subparsers)
    clear_checkpoint.init(securitydata_subparsers)
