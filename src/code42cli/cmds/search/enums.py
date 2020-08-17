from code42cli.output_formats import OutputFormat

IS_CHECKPOINT_KEY = "use_checkpoint"


class SecurityDataOutputFormat(OutputFormat):
    CEF = "CEF"

    def __iter__(self):
        return iter([self.TABLE, self.CSV, self.JSON, self.RAW, self.CEF])


class AlertSeverity:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.HIGH, self.MEDIUM, self.LOW]


class AlertState:
    OPEN = "OPEN"
    DISMISSED = "RESOLVED"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [self.OPEN, self.DISMISSED]


class ExposureType:
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


class RuleType:
    ENDPOINT_EXFILTRATION = "FedEndpointExfiltration"
    CLOUD_SHARE_PERMISSIONS = "FedCloudSharePermissions"
    FILE_TYPE_MISMATCH = "FedFileTypeMismatch"

    def __iter__(self):
        return iter(self._as_list())

    def __len__(self):
        return len(self._as_list())

    def _as_list(self):
        return [
            self.ENDPOINT_EXFILTRATION,
            self.CLOUD_SHARE_PERMISSIONS,
            self.FILE_TYPE_MISMATCH,
        ]


class ServerProtocol:
    TCP = "TCP"
    UDP = "UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])
