from code42cli.securitydata.options import ExposureType


def add_arguments_to_parser(parser):
    _add_advanced_query(parser)
    _add_begin_date_arg(parser)
    _add_end_date_arg(parser)
    _add_exposure_types_arg(parser)
    _add_username_arg(parser)
    _add_actor_arg(parser)
    _add_md5_arg(parser)
    _add_sha256_arg(parser)
    _add_source_arg(parser)
    _add_filename_arg(parser)
    _add_filepath_arg(parser)
    _add_process_owner_arg(parser)
    _add_tab_url_arg(parser)
    _add_include_non_exposure_arg(parser)


class SearchArguments(object):
    ADVANCED_QUERY = u"advanced_query"
    BEGIN_DATE = u"begin_date"
    END_DATE = u"end_date"
    EXPOSURE_TYPES = u"exposure_types"
    C42USERNAME = u"c42usernames"
    ACTOR = u"actors"
    MD5 = u"md5_hashes"
    SHA256 = u"sha256_hashes"
    SOURCE = u"sources"
    FILENAME = u"filenames"
    FILEPATH = u"filepaths"
    PROCESS_OWNER = u"process_owners"
    TAB_URL = u"tab_urls"
    INCLUDE_NON_EXPOSURE_EVENTS = u"include_non_exposure_events"

    def __iter__(self):
        return iter(
            [
                self.ADVANCED_QUERY,
                self.BEGIN_DATE,
                self.END_DATE,
                self.EXPOSURE_TYPES,
                self.C42USERNAME,
                self.ACTOR,
                self.MD5,
                self.SHA256,
                self.SOURCE,
                self.FILENAME,
                self.FILEPATH,
                self.PROCESS_OWNER,
                self.TAB_URL,
                self.INCLUDE_NON_EXPOSURE_EVENTS,
            ]
        )


def _add_advanced_query(parser):
    parser.add_argument(
        u"--advanced-query",
        action=u"store",
        dest=SearchArguments.ADVANCED_QUERY,
        help=u"A raw JSON file event query. "
        u"Useful for when the provided query parameters do not satisfy your requirements."
        u"WARNING: Using advanced queries ignores all other query parameters.",
    )


def _add_begin_date_arg(parser):
    parser.add_argument(
        u"-b",
        u"--begin",
        action=u"store",
        dest=SearchArguments.BEGIN_DATE,
        help=u"The beginning of the date range in which to look for events, "
        u"in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format.",
    )


def _add_end_date_arg(parser):
    parser.add_argument(
        u"-e",
        u"--end",
        action=u"store",
        dest=SearchArguments.END_DATE,
        help=u"The end of the date range in which to look for events, "
        u"in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format.",
    )


def _add_exposure_types_arg(parser):
    parser.add_argument(
        u"-t",
        u"--types",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.EXPOSURE_TYPES,
        help=u"Limits events to those with given exposure types. "
        u"Available choices={0}".format(list(ExposureType())),
    )


def _add_username_arg(parser):
    parser.add_argument(
        u"--c42username",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.C42USERNAME,
        help=u"Limits events to endpoint events for these users.",
    )


def _add_actor_arg(parser):
    parser.add_argument(
        u"--actor",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.ACTOR,
        help=u"Limits events to only those enacted by the cloud service user of the person who caused the event.",
    )


def _add_md5_arg(parser):
    parser.add_argument(
        u"--md5",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.MD5,
        help=u"Limits events to file events where the file has one of these MD5 hashes.",
    )


def _add_sha256_arg(parser):
    parser.add_argument(
        u"--sha256",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.SHA256,
        help=u"Limits events to file events where the file has one of these SHA256 hashes.",
    )


def _add_source_arg(parser):
    parser.add_argument(
        u"--source",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.SOURCE,
        help=u"Limits events to only those from one of these sources. Example=Gmail.",
    )


def _add_filename_arg(parser):
    parser.add_argument(
        u"--filename",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.FILENAME,
        help=u"Limits events to file events where the file has one of these names.",
    )


def _add_filepath_arg(parser):
    parser.add_argument(
        u"--filepath",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.FILEPATH,
        help=u"Limits events to file events where the file is located at one of these paths.",
    )


def _add_process_owner_arg(parser):
    parser.add_argument(
        u"--processOwner",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.PROCESS_OWNER,
        help=u"Limits events to exposure events where one of these users "
        u"owns the process behind the exposure.",
    )


def _add_tab_url_arg(parser):
    parser.add_argument(
        u"--tabURL",
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.TAB_URL,
        help=u"Limits events to be exposure events with one of these destination tab URLs.",
    )


def _add_include_non_exposure_arg(parser):
    parser.add_argument(
        u"--include-non-exposure",
        action=u"store_true",
        dest=SearchArguments.INCLUDE_NON_EXPOSURE_EVENTS,
        help=u"Get all events including non-exposure events.",
    )
