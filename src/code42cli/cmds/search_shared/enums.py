IS_INCREMENTAL_KEY = u"incremental"


class OutputFormat(object):
    CEF = u"CEF"
    JSON = u"JSON"
    RAW = u"RAW-JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class AlertOutputFormat(object):
    JSON = u"JSON"
    RAW = u"RAW-JSON"

    def __iter__(self):
        return iter([self.JSON, self.RAW])


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


class RuleType(object):
    ENDPOINT_EXFILTRATION = u"FedEndpointExfiltration"
    CLOUD_SHARE_PERMISSIONS = u"FedCloudSharePermissions"
    FILE_TYPE_MISMATCH = u"FedFileTypeMismatch"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.ENDPOINT_EXFILTRATION, self.CLOUD_SHARE_PERMISSIONS, self.FILE_TYPE_MISMATCH]


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

    def __iter__(self):
        return iter([self.ADVANCED_QUERY, self.BEGIN_DATE, self.END_DATE])


class FileEventFilterArguments(SearchArguments):
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


class AlertFilterArguments(object):
    STATE = u"state"
    SEVERITY = u"severity"
    ACTOR = u"actor"
    ACTOR_CONTAINS = u"actor_contains"
    EXCLUDE_ACTOR = u"exclude_actor"
    EXCLUDE_ACTOR_CONTAINS = u"exclude_actor_contains"
    RULE_NAME = u"rule_name"
    EXCLUDE_RULE_NAME = u"exclude_rule_name"
    RULE_ID = u"rule_id"
    EXCLUDE_RULE_ID = u"exclude_rule_id"
    RULE_TYPE = u"rule_type"
    EXCLUDE_RULE_TYPE = u"exclude_rule_type"
    DESCRIPTION = u"description"

    def __iter__(self):
        return iter(
            [
                self.STATE,
                self.SEVERITY,
                self.ACTOR,
                self.ACTOR_CONTAINS,
                self.EXCLUDE_ACTOR,
                self.EXCLUDE_ACTOR_CONTAINS,
                self.RULE_NAME,
                self.EXCLUDE_RULE_NAME,
                self.RULE_ID,
                self.EXCLUDE_RULE_ID,
                self.RULE_TYPE,
                self.EXCLUDE_RULE_TYPE,
                self.DESCRIPTION,
            ]
        )
