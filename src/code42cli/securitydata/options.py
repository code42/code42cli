class OutputFormat(object):
    CEF = "CEF"
    JSON = "JSON"
    RAW = "RAW-JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON, self.RAW])


class ExposureType(object):
    SHARED_VIA_LINK = "SharedViaLink"
    SHARED_TO_DOMAIN = "SharedToDomain"
    APPLICATION_READ = "ApplicationRead"
    CLOUD_STORAGE = "CloudStorage"
    REMOVABLE_MEDIA = "RemovableMedia"
    IS_PUBLIC = "IsPublic"

    def __iter__(self):
        return iter(
            [
                self.SHARED_VIA_LINK,
                self.SHARED_TO_DOMAIN,
                self.APPLICATION_READ,
                self.CLOUD_STORAGE,
                self.REMOVABLE_MEDIA,
                self.IS_PUBLIC,
            ]
        )


class ServerProtocol(object):
    TCP = "TCP"
    UDP = "UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])
