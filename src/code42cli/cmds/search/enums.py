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
