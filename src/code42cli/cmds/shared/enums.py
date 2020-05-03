IS_INCREMENTAL_KEY = u"incremental"


class OutputFormat(object):
    CEF = u"CEF"
    JSON = u"JSON"
    RAW = u"RAW-JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class AlertSeverity(object):
    HIGH = u"HIGH"
    MEDIUM = u"MEDIUM"
    LOW = u"LOW"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.HIGH, self.MEDIUM, self.LOW]


class AlertState(object):
    OPEN = u"OPEN"
    DISMISSED = u"RESOLVED"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.OPEN, self.DISMISSED]


class ExposureType(object):
    SHARED_VIA_LINK = u"SharedViaLink"
    SHARED_TO_DOMAIN = u"SharedToDomain"
    APPLICATION_READ = u"ApplicationRead"
    CLOUD_STORAGE = u"CloudStorage"
    REMOVABLE_MEDIA = u"RemovableMedia"
    IS_PUBLIC = u"IsPublic"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [
            self.SHARED_VIA_LINK,
            self.SHARED_TO_DOMAIN,
            self.APPLICATION_READ,
            self.CLOUD_STORAGE,
            self.REMOVABLE_MEDIA,
            self.IS_PUBLIC,
        ]


class ServerProtocol(object):
    TCP = u"TCP"
    UDP = u"UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])


class SearchArguments(object):
    """These string values should match `argparse` stored parameter names. For example, for the 
    CLI argument `--c42-username`, the string should be `c42_username`."""

    ADVANCED_QUERY = u"advanced_query"
    BEGIN_DATE = u"begin"
    END_DATE = u"end"
    EXPOSURE_TYPES = u"type"
    C42_USERNAME = u"c42_username"
    ACTOR = u"actor"
    MD5 = u"md5"
    SHA256 = u"sha256"
    SOURCE = u"source"
    FILE_NAME = u"file_name"
    FILE_PATH = u"file_path"
    PROCESS_OWNER = u"process_owner"
    TAB_URL = u"tab_url"
    INCLUDE_NON_EXPOSURE_EVENTS = u"include_non_exposure"

    def __iter__(self):
        return iter(
            [
                self.ADVANCED_QUERY,
                self.BEGIN_DATE,
                self.END_DATE,
                self.EXPOSURE_TYPES,
                self.C42_USERNAME,
                self.ACTOR,
                self.MD5,
                self.SHA256,
                self.SOURCE,
                self.FILE_NAME,
                self.FILE_PATH,
                self.PROCESS_OWNER,
                self.TAB_URL,
                self.INCLUDE_NON_EXPOSURE_EVENTS,
            ]
        )


class AlertArguments(object):

    ADVANCED_QUERY = u"advanced_query"
    BEGIN_DATE = u"begin"
    END_DATE = u"end"
    STATE = u"state"
    SEVERITY = u"severity"
    ACTOR_IS = u"actor_is"
    ACTOR_CONTAINS = u"actor_contains"
    ACTOR_NOT = u"actor_not"
    ACTOR_NOT_CONTAINS = u"actor_not_contains"
    RULE_NAME_IS = u"rule_name_is"
    RULE_NAME_CONTAINS = u"rule_name_contains"
    RULE_NAME_NOT = u"rule_name_not"
    RULE_NAME_NOT_CONTAINS = u"rule_name_not_contains"
    DESCRIPTION = u"description"

    def __iter__(self):
        return iter(
            [
                self.ADVANCED_QUERY,
                self.BEGIN_DATE,
                self.END_DATE,
                self.STATE,
                self.SEVERITY,
                self.ACTOR_IS,
                self.ACTOR_CONTAINS,
                self.ACTOR_NOT,
                self.ACTOR_NOT_CONTAINS,
                self.RULE_NAME_IS,
                self.RULE_NAME_CONTAINS,
                self.RULE_NAME_NOT,
                self.RULE_NAME_NOT_CONTAINS,
                self.DESCRIPTION,
            ]
        )
