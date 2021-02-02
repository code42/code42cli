import json
import logging

import pytest


AED_CLOUD_ACTIVITY_EVENT_DICT = json.loads(
    """{
    "url": "https://www.example.com",
    "syncDestination": "TEST_SYNC_DESTINATION",
    "sharedWith": [{"cloudUsername": "example1@example.com"}, {"cloudUsername": "example2@example.com"}],
    "cloudDriveId": "TEST_CLOUD_DRIVE_ID",
    "actor": "actor@example.com",
    "tabUrl": "TEST_TAB_URL",
    "windowTitle": "TEST_WINDOW_TITLE"
    }"""
)
AED_REMOVABLE_MEDIA_EVENT_DICT = json.loads(
    """{
    "removableMediaVendor": "TEST_VENDOR_NAME",
    "removableMediaName": "TEST_NAME",
    "removableMediaSerialNumber": "TEST_SERIAL_NUMBER",
    "removableMediaCapacity": 5000000,
    "removableMediaBusType": "TEST_BUS_TYPE"
    }"""
)
AED_EMAIL_EVENT_DICT = json.loads(
    """{
    "emailSender": "TEST_EMAIL_SENDER",
    "emailRecipients": ["test.recipient1@example.com", "test.recipient2@example.com"]
    }"""
)
AED_EVENT_DICT = json.loads(
    """{
    "eventId": "0_1d71796f-af5b-4231-9d8e-df6434da4663_912339407325443353_918253081700247636_16",
    "eventType": "READ_BY_APP",
    "eventTimestamp": "2019-09-09T02:42:23.851Z",
    "insertionTimestamp": "2019-09-09T22:47:42.724Z",
    "filePath": "/Users/testtesterson/Downloads/About Downloads.lpdf/Contents/Resources/English.lproj/",
    "fileName": "InfoPlist.strings",
    "fileType": "FILE",
    "fileCategory": "UNCATEGORIZED",
    "fileSize": 86,
    "fileOwner": "testtesterson",
    "md5Checksum": "19b92e63beb08c27ab4489fcfefbbe44",
    "sha256Checksum": "2e0677355c37fa18fd20d372c7420b8b34de150c5801910c3bbb1e8e04c727ef",
    "createTimestamp": "2012-07-22T02:19:29Z",
    "modifyTimestamp": "2012-12-19T03:00:08Z",
    "deviceUserName": "test.testerson+testair@example.com",
    "osHostName": "Test's MacBook Air",
    "domainName": "192.168.0.3",
    "publicIpAddress": "71.34.4.22",
    "privateIpAddresses": [
        "fe80:0:0:0:f053:a9bd:973:6c8c%utun1",
        "fe80:0:0:0:a254:cb31:8840:9d6b%utun0",
        "0:0:0:0:0:0:0:1%lo0",
        "192.168.0.3",
        "fe80:0:0:0:0:0:0:1%lo0",
        "fe80:0:0:0:8c28:1ac9:5745:a6e7%utun3",
        "fe80:0:0:0:2e4a:351c:bb9b:2f28%utun2",
        "fe80:0:0:0:6df:855c:9436:37f8%utun4",
        "fe80:0:0:0:ce:5072:e5f:7155%en0",
        "fe80:0:0:0:b867:afff:fefc:1a82%awdl0",
        "127.0.0.1"
    ],
    "deviceUid": "912339407325443353",
    "userUid": "912338501981077099",
    "actor": null,
    "directoryId": [],
    "source": "Endpoint",
    "url": null,
    "shared": null,
    "sharedWith": [],
    "sharingTypeAdded": [],
    "cloudDriveId": null,
    "detectionSourceAlias": null,
    "fileId": null,
    "exposure": [
        "ApplicationRead"
    ],
    "processOwner": "testtesterson",
    "processName": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "removableMediaVendor": null,
    "removableMediaName": null,
    "removableMediaSerialNumber": null,
    "removableMediaCapacity": null,
    "removableMediaBusType": null,
    "syncDestination": null
    }"""
)


@pytest.fixture()
def mock_log_record(mocker):
    return mocker.MagicMock(spec=logging.LogRecord)


@pytest.fixture
def mock_file_event_log_record(mock_log_record):
    mock_log_record.msg = AED_EVENT_DICT
    return mock_log_record


@pytest.fixture
def mock_file_event_removable_media_event_log_record(mock_log_record):
    mock_log_record.msg = AED_REMOVABLE_MEDIA_EVENT_DICT
    return mock_log_record


@pytest.fixture
def mock_file_event_cloud_activity_event_log_record(mock_log_record):
    mock_log_record.msg = AED_CLOUD_ACTIVITY_EVENT_DICT
    return mock_log_record


@pytest.fixture
def mock_file_event_email_event_log_record(mock_log_record):
    mock_log_record.msg = AED_EMAIL_EVENT_DICT
    return mock_log_record
