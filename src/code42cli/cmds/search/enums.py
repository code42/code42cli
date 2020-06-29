IS_CHECKPOINT_KEY = "use_checkpoint"


class OutputFormat(object):
    CEF = "CEF"
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class AlertOutputFormat(object):
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.JSON, self.RAW])


class AlertSeverity(object):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.HIGH, self.MEDIUM, self.LOW]


class AlertState(object):
    OPEN = "OPEN"
    DISMISSED = "RESOLVED"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.OPEN, self.DISMISSED]


class ExposureType(object):
    SHARED_VIA_LINK = "SharedViaLink"
    SHARED_TO_DOMAIN = "SharedToDomain"
    APPLICATION_READ = "ApplicationRead"
    CLOUD_STORAGE = "CloudStorage"
    REMOVABLE_MEDIA = "RemovableMedia"
    IS_PUBLIC = "IsPublic"

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
    ENDPOINT_EXFILTRATION = "FedEndpointExfiltration"
    CLOUD_SHARE_PERMISSIONS = "FedCloudSharePermissions"
    FILE_TYPE_MISMATCH = "FedFileTypeMismatch"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.ENDPOINT_EXFILTRATION, self.CLOUD_SHARE_PERMISSIONS, self.FILE_TYPE_MISMATCH]


class ServerProtocol(object):
    TCP = "TCP"
    UDP = "UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])


class SearchArguments(object):
    """These string values should match `argparse` stored parameter names. For example, for the 
    CLI argument `--c42-username`, the string should be `c42_username`."""

    ADVANCED_QUERY = "advanced_query"
    BEGIN_DATE = "begin"
    END_DATE = "end"

    def __iter__(self):
        return iter([self.ADVANCED_QUERY, self.BEGIN_DATE, self.END_DATE])


class FileEventFilterArguments(SearchArguments):
    EXPOSURE_TYPES = "type"
    C42_USERNAME = "c42_username"
    ACTOR = "actor"
    MD5 = "md5"
    SHA256 = "sha256"
    SOURCE = "source"
    FILE_NAME = "file_name"
    FILE_PATH = "file_path"
    PROCESS_OWNER = "process_owner"
    TAB_URL = "tab_url"
    INCLUDE_NON_EXPOSURE_EVENTS = "include_non_exposure"

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
    STATE = "state"
    SEVERITY = "severity"
    ACTOR = "actor"
    ACTOR_CONTAINS = "actor_contains"
    EXCLUDE_ACTOR = "exclude_actor"
    EXCLUDE_ACTOR_CONTAINS = "exclude_actor_contains"
    RULE_NAME = "rule_name"
    EXCLUDE_RULE_NAME = "exclude_rule_name"
    RULE_ID = "rule_id"
    EXCLUDE_RULE_ID = "exclude_rule_id"
    RULE_TYPE = "rule_type"
    EXCLUDE_RULE_TYPE = "exclude_rule_type"
    DESCRIPTION = "description"

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
