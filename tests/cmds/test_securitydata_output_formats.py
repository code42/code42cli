import json

import pytest
from c42eventextractor.maps import FILE_EVENT_TO_SIGNATURE_ID_MAP

from code42cli.cmds.search.enums import FileEventsOutputFormat
from code42cli.cmds.securitydata_output_formats import FileEventsOutputFormatter
from code42cli.cmds.securitydata_output_formats import to_cef


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
    "deviceUserName": "test.testerson+testair@code42.com",
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


@pytest.fixture
def mock_file_event_removable_media_event():
    return AED_REMOVABLE_MEDIA_EVENT_DICT


@pytest.fixture
def mock_file_event_cloud_activity_event():
    return AED_CLOUD_ACTIVITY_EVENT_DICT


@pytest.fixture
def mock_file_event_email_event():
    return AED_EMAIL_EVENT_DICT


@pytest.fixture
def mock_file_event():
    return AED_EVENT_DICT


@pytest.fixture
def mock_to_cef(mocker):
    return mocker.patch("code42cli.cmds.securitydata_output_formats.to_cef")


class TestFileEventsOutputFormatter:
    def test_init_sets_format_func_to_dynamic_csv_function_when_csv_option_is_passed(
        self, mock_to_csv
    ):
        formatter = FileEventsOutputFormatter(FileEventsOutputFormat.CSV)
        for _ in formatter.get_formatted_output("TEST"):
            pass
        mock_to_csv.assert_called_once_with("TEST")

    def test_init_sets_format_func_to_formatted_json_function_when_json__option_is_passed(
        self, mock_to_formatted_json
    ):
        formatter = FileEventsOutputFormatter(FileEventsOutputFormat.JSON)
        for _ in formatter.get_formatted_output(["TEST"]):
            pass
        mock_to_formatted_json.assert_called_once_with("TEST")

    def test_init_sets_format_func_to_json_function_when_raw_json_format_option_is_passed(
        self, mock_to_json
    ):
        formatter = FileEventsOutputFormatter(FileEventsOutputFormat.RAW)
        for _ in formatter.get_formatted_output(["TEST"]):
            pass
        mock_to_json.assert_called_once_with("TEST")

    def test_init_sets_format_func_to_cef_function_when_cef_format_option_is_passed(
        self, mock_to_cef
    ):
        formatter = FileEventsOutputFormatter(FileEventsOutputFormat.CEF)
        for _ in formatter.get_formatted_output(["TEST"]):
            pass
        mock_to_cef.assert_called_once_with("TEST")

    def test_init_sets_format_func_to_table_function_when_table_format_option_is_passed(
        self, mock_to_table
    ):
        formatter = FileEventsOutputFormatter(FileEventsOutputFormat.TABLE)
        for _ in formatter.get_formatted_output("TEST"):
            pass
        mock_to_table.assert_called_once_with("TEST", None)

    def test_init_sets_format_func_to_table_function_when_no_format_option_is_passed(
        self, mock_to_table
    ):
        formatter = FileEventsOutputFormatter(None)
        for _ in formatter.get_formatted_output("TEST"):
            pass
        mock_to_table.assert_called_once_with("TEST", None)


def test_to_cef_returns_cef_tagged_string(mock_file_event):
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[0] == "CEF:0"


def test_to_cef_uses_correct_vendor_name(mock_file_event):
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[1] == "Code42"


def test_to_cef_uses_correct_default_product_name(mock_file_event):
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[2] == "Advanced Exfiltration Detection"


def test_to_cef_uses_correct_default_severity(mock_file_event):
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    assert cef_parts[6] == "5"


def test_to_cef_excludes_none_values_from_output(mock_file_event):
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    assert "=None " not in cef_parts[-1]


def test_to_cef_excludes_empty_values_from_output(mock_file_event):
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    assert "= " not in cef_parts[-1]


def test_to_cef_excludes_file_event_fields_not_in_cef_map(mock_file_event):
    test_value = "definitelyExcludedValue"
    mock_file_event["unmappedFieldName"] = test_value
    cef_out = to_cef(mock_file_event)
    cef_parts = get_cef_parts(cef_out)
    del mock_file_event["unmappedFieldName"]
    assert test_value not in cef_parts[-1]


def test_to_cef_includes_os_hostname_if_present(mock_file_event):
    expected_field_name = "shost"
    expected_value = "Test's MacBook Air"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_public_ip_address_if_present(mock_file_event):
    expected_field_name = "src"
    expected_value = "71.34.4.22"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_user_uid_if_present(mock_file_event):
    expected_field_name = "suid"
    expected_value = "912338501981077099"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_device_username_if_present(mock_file_event):
    expected_field_name = "suser"
    expected_value = "test.testerson+testair@code42.com"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_capacity_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cn1"
    expected_value = "5000000"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_capacity_label_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cn1Label"
    expected_value = "Code42AEDRemovableMediaCapacity"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_bus_type_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs1"
    expected_value = "TEST_BUS_TYPE"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_bus_type_label_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs1Label"
    expected_value = "Code42AEDRemovableMediaBusType"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_vendor_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs2"
    expected_value = "TEST_VENDOR_NAME"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_vendor_label_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs2Label"
    expected_value = "Code42AEDRemovableMediaVendor"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_name_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs3"
    expected_value = "TEST_NAME"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_name_label_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs3Label"
    expected_value = "Code42AEDRemovableMediaName"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_serial_number_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs4"
    expected_value = "TEST_SERIAL_NUMBER"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_removable_media_serial_number_label_if_present(
    mock_file_event_removable_media_event,
):
    expected_field_name = "cs4Label"
    expected_value = "Code42AEDRemovableMediaSerialNumber"
    cef_out = to_cef(mock_file_event_removable_media_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_actor_if_present(mock_file_event_cloud_activity_event,):
    expected_field_name = "suser"
    expected_value = "actor@example.com"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_sync_destination_if_present(
    mock_file_event_cloud_activity_event,
):
    expected_field_name = "destinationServiceName"
    expected_value = "TEST_SYNC_DESTINATION"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_event_timestamp_if_present(mock_file_event):
    expected_field_name = "end"
    expected_value = "1567996943851"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_create_timestamp_if_present(mock_file_event):
    expected_field_name = "fileCreateTime"
    expected_value = "1342923569000"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_md5_checksum_if_present(mock_file_event):
    expected_field_name = "fileHash"
    expected_value = "19b92e63beb08c27ab4489fcfefbbe44"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_modify_timestamp_if_present(mock_file_event):
    expected_field_name = "fileModificationTime"
    expected_value = "1355886008000"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_path_if_present(mock_file_event):
    expected_field_name = "filePath"
    expected_value = "/Users/testtesterson/Downloads/About Downloads.lpdf/Contents/Resources/English.lproj/"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_name_if_present(mock_file_event):
    expected_field_name = "fname"
    expected_value = "InfoPlist.strings"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_size_if_present(mock_file_event):
    expected_field_name = "fsize"
    expected_value = "86"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_file_category_if_present(mock_file_event):
    expected_field_name = "fileType"
    expected_value = "UNCATEGORIZED"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_exposure_if_present(mock_file_event):
    expected_field_name = "reason"
    expected_value = "ApplicationRead"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_url_if_present(mock_file_event_cloud_activity_event,):
    expected_field_name = "filePath"
    expected_value = "https://www.example.com"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_insertion_timestamp_if_present(mock_file_event):
    expected_field_name = "rt"
    expected_value = "1568069262724"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_process_name_if_present(mock_file_event):
    expected_field_name = "sproc"
    expected_value = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_event_id_if_present(mock_file_event):
    expected_field_name = "externalId"
    expected_value = "0_1d71796f-af5b-4231-9d8e-df6434da4663_912339407325443353_918253081700247636_16"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_device_uid_if_present(mock_file_event):
    expected_field_name = "deviceExternalId"
    expected_value = "912339407325443353"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_domain_name_if_present(mock_file_event):
    expected_field_name = "dvchost"
    expected_value = "192.168.0.3"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_source_if_present(mock_file_event):
    expected_field_name = "sourceServiceName"
    expected_value = "Endpoint"
    cef_out = to_cef(mock_file_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_cloud_drive_id_if_present(
    mock_file_event_cloud_activity_event,
):
    expected_field_name = "aid"
    expected_value = "TEST_CLOUD_DRIVE_ID"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_shared_with_if_present(mock_file_event_cloud_activity_event,):
    expected_field_name = "duser"
    expected_value = "example1@example.com,example2@example.com"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_tab_url_if_present(mock_file_event_cloud_activity_event,):
    expected_field_name = "request"
    expected_value = "TEST_TAB_URL"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_window_title_if_present(mock_file_event_cloud_activity_event,):
    expected_field_name = "requestClientApplication"
    expected_value = "TEST_WINDOW_TITLE"
    cef_out = to_cef(mock_file_event_cloud_activity_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_email_recipients_if_present(mock_file_event_email_event,):
    expected_field_name = "duser"
    expected_value = "test.recipient1@example.com,test.recipient2@example.com"
    cef_out = to_cef(mock_file_event_email_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_email_sender_if_present(mock_file_event_email_event,):
    expected_field_name = "suser"
    expected_value = "TEST_EMAIL_SENDER"
    cef_out = to_cef(mock_file_event_email_event)
    assert key_value_pair_in_cef_extension(expected_field_name, expected_value, cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_created(
    mock_file_event,
):
    event_type = "CREATED"
    mock_file_event["eventType"] = event_type
    cef_out = to_cef(mock_file_event)
    assert event_name_assigned_correct_signature_id(event_type, "C42200", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_modified(
    mock_file_event,
):
    event_type = "MODIFIED"
    mock_file_event["eventType"] = event_type
    cef_out = to_cef(mock_file_event)
    assert event_name_assigned_correct_signature_id(event_type, "C42201", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_deleted(
    mock_file_event,
):
    event_type = "DELETED"
    mock_file_event["eventType"] = event_type
    cef_out = to_cef(mock_file_event)
    assert event_name_assigned_correct_signature_id(event_type, "C42202", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_read_by_app(
    mock_file_event,
):
    event_type = "READ_BY_APP"
    mock_file_event["eventType"] = event_type
    cef_out = to_cef(mock_file_event)
    assert event_name_assigned_correct_signature_id(event_type, "C42203", cef_out)


def test_to_cef_includes_correct_event_name_and_signature_id_for_emailed(
    mock_file_event_email_event,
):
    event_type = "EMAILED"
    mock_file_event_email_event["eventType"] = event_type
    cef_out = to_cef(mock_file_event_email_event)
    assert event_name_assigned_correct_signature_id(event_type, "C42204", cef_out)


def get_cef_parts(cef_str):
    return cef_str.split("|")


def key_value_pair_in_cef_extension(field_name, field_value, cef_str):
    cef_parts = get_cef_parts(cef_str)
    kvp = "{}={}".format(field_name, field_value)
    return kvp in cef_parts[-1]


def event_name_assigned_correct_signature_id(event_name, signature_id, cef_out):
    if event_name in FILE_EVENT_TO_SIGNATURE_ID_MAP:
        cef_parts = get_cef_parts(cef_out)
        return cef_parts[4] == signature_id and cef_parts[5] == event_name

    return False
