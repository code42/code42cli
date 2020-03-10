PROFILE_NAME_KEY = u"profile_name"
PROFILE_HELP_MESSAGE = (
    u"The name of the profile containing your Code42 username and authority host address."
)


def add_arguments_to_parser(parser):
    add_debug_arg(parser)
    add_profile_name_arg(parser)


def add_debug_arg(parser):
    parser.add_argument(
        u"-d",
        u"--debug",
        dest=u"is_debug_mode",
        action=u"store_true",
        help=u"Turn on Debug logging.",
    )


def add_profile_name_arg(parser):
    parser.add_argument(
        u"--profile", action=u"store", dest=PROFILE_NAME_KEY, help=PROFILE_HELP_MESSAGE
    )
