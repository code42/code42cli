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
    C42USERNAME = u"c42username"
    ACTOR = u"actor"
    MD5 = u"md5"
    SHA256 = u"sha256"
    SOURCE = u"source"
    FILENAME = u"filename"
    FILEPATH = u"filepath"
    PROCESS_OWNER = u"process_owner"
    TAB_URL = u"tab_url"
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
        nargs=u"+",
        action=u"store",
        dest=SearchArguments.BEGIN_DATE,
        help=u"The beginning of the date range in which to look for events, "
        u"in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format.",
    )


def _add_end_date_arg(parser):
    parser.add_argument(
        u"-e",
        u"--end",
        nargs=u"+",
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
        action=u"store",
        dest=SearchArguments.C42USERNAME,
        help=u"Limits events to endpoint events for this user.",
    )


def _add_actor_arg(parser):
    parser.add_argument(
        u"--actor",
        action=u"store",
        dest=SearchArguments.ACTOR,
        help=u"Limits events to only those enacted by this actor.",
    )


def _add_md5_arg(parser):
    parser.add_argument(
        u"--md5",
        action=u"store",
        dest=SearchArguments.MD5,
        help=u"Limits events to file events where the file has this MD5 hash.",
    )


def _add_sha256_arg(parser):
    parser.add_argument(
        u"--sha256",
        action=u"store",
        dest=SearchArguments.SHA256,
        help=u"Limits events to file events where the file has this SHA256 hash.",
    )


def _add_source_arg(parser):
    parser.add_argument(
        u"--source",
        action=u"store",
        dest=SearchArguments.SOURCE,
        help=u"Limits events to only those from this source. Example=Gmail.",
    )


def _add_filename_arg(parser):
    parser.add_argument(
        u"--filename",
        action=u"store",
        dest=SearchArguments.FILENAME,
        help=u"Limits events to file events where the file has this name.",
    )


def _add_filepath_arg(parser):
    parser.add_argument(
        u"--filepath",
        action=u"store",
        dest=SearchArguments.FILEPATH,
        help=u"Limits events to file events where the file is located at this path.",
    )


def _add_process_owner_arg(parser):
    parser.add_argument(
        u"--processOwner",
        action=u"store",
        dest=SearchArguments.PROCESS_OWNER,
        help=u"Limits events to exposure events where this user "
        u"owns the process behind the exposure.",
    )


def _add_tab_url_arg(parser):
    parser.add_argument(
        u"--tabURL",
        action=u"store",
        dest=SearchArguments.TAB_URL,
        help=u"Limits events to be exposure events with this destination tab URL.",
    )


def _add_include_non_exposure_arg(parser):
    parser.add_argument(
        u"--include-non-exposure",
        action=u"store_true",
        dest=SearchArguments.INCLUDE_NON_EXPOSURE_EVENTS,
        help=u"Get all events including non-exposure events.",
    )
