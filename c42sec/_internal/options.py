class OutputFormat(object):
    CEF = "CEF"
    JSON = "JSON"

    def __iter__(self):
        return iter([self.CEF, self.JSON])


class ExposureType(object):
    SHARED_VIA_LINK = u"SharedViaLink"
    SHARED_TO_DOMAIN = u"SharedToDomain"
    APPLICATION_READ = u"ApplicationRead"
    CLOUD_STORAGE = u"CloudStorage"
    REMOVABLE_MEDIA = u"RemovableMedia"
    IS_PUBLIC = u"IsPublic"

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
