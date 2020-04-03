IS_INCREMENTAL_KEY = u"incremental"


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
    TCP = "TCP"
    UDP = "UDP"

    def __iter__(self):
        return iter([self.TCP, self.UDP])


class SearchArguments(object):
    ADVANCED_QUERY = u"advanced_query"
    BEGIN_DATE = u"begin"
    END_DATE = u"end"
    EXPOSURE_TYPES = u"type"
    C42USERNAME = u"c42username"
    ACTOR = u"actor"
    MD5 = u"md5"
    SHA256 = u"sha256"
    SOURCE = u"source"
    FILENAME = u"filename"
    FILEPATH = u"filepath"
    PROCESS_OWNER = u"processOwner"
    TAB_URL = u"tabURL"
    INCLUDE_NON_EXPOSURE_EVENTS = u"include_non_exposure"

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
