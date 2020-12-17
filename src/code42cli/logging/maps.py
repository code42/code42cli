JSON_TO_CEF_MAP = {
    "actor": "suser",
    "cloudDriveId": "aid",
    "createTimestamp": "fileCreateTime",
    "deviceUid": "deviceExternalId",
    "deviceUserName": "suser",
    "domainName": "dvchost",
    "emailRecipients": "duser",
    "emailSender": "suser",
    "eventId": "externalId",
    "eventTimestamp": "end",
    "exposure": "reason",
    "fileCategory": "fileType",
    "fileName": "fname",
    "filePath": "filePath",
    "fileSize": "fsize",
    "insertionTimestamp": "rt",
    "md5Checksum": "fileHash",
    "modifyTimestamp": "fileModificationTime",
    "osHostName": "shost",
    "processName": "sproc",
    "processOwner": "spriv",
    "publicIpAddress": "src",
    "removableMediaBusType": "cs1",
    "removableMediaCapacity": "cn1",
    "removableMediaName": "cs3",
    "removableMediaSerialNumber": "cs4",
    "removableMediaVendor": "cs2",
    "sharedWith": "duser",
    "source": "sourceServiceName",
    "syncDestination": "destinationServiceName",
    "tabUrl": "request",
    "url": "filePath",
    "userUid": "suid",
    "windowTitle": "requestClientApplication",
}

CEF_CUSTOM_FIELD_NAME_MAP = {
    "cn1Label": "Code42AEDRemovableMediaCapacity",
    "cs1Label": "Code42AEDRemovableMediaBusType",
    "cs2Label": "Code42AEDRemovableMediaVendor",
    "cs3Label": "Code42AEDRemovableMediaName",
    "cs4Label": "Code42AEDRemovableMediaSerialNumber",
}

FILE_EVENT_TO_SIGNATURE_ID_MAP = {
    "CREATED": "C42200",
    "MODIFIED": "C42201",
    "DELETED": "C42202",
    "READ_BY_APP": "C42203",
    "EMAILED": "C42204",
}
