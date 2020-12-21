import json

from code42cli.logger.formatters import FileEventDictToCEFFormatter
from code42cli.logger.formatters import FileEventDictToJSONFormatter
from code42cli.logger.formatters import FileEventDictToRawJSONFormatter
from code42cli.logger.maps import FILE_EVENT_TO_SIGNATURE_ID_MAP


class TestFileEventDictToCEFFormatter:
    def test_format_returns_cef_tagged_string(self, mock_file_event_log_record):
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert cef_parts[0] == "CEF:0"

    def test_format_uses_correct_vendor_name(self, mock_file_event_log_record):
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert cef_parts[1] == "Code42"

    def test_format_uses_correct_default_product_name(self, mock_file_event_log_record):
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert cef_parts[2] == "Advanced Exfiltration Detection"

    def test_format_uses_correct_product_name(self, mock_file_event_log_record):
        alternate_product_name = "Security Parser Formatter Extractor Thingamabob"
        cef_out = FileEventDictToCEFFormatter(
            default_product_name=alternate_product_name
        ).format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert cef_parts[2] == alternate_product_name

    def test_format_uses_correct_default_severity(self, mock_file_event_log_record):
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert cef_parts[6] == "5"

    def test_format_uses_correct_severity(self, mock_file_event_log_record):
        alternate_severity = "7"
        cef_out = FileEventDictToCEFFormatter(
            default_severity_level=alternate_severity
        ).format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert cef_parts[6] == alternate_severity

    def test_format_excludes_none_values_from_output(self, mock_file_event_log_record):
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert "=None " not in cef_parts[-1]

    def test_format_excludes_empty_values_from_output(self, mock_file_event_log_record):
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        assert "= " not in cef_parts[-1]

    def test_format_excludes_file_event_fields_not_in_cef_map(
        self, mock_file_event_log_record
    ):
        test_value = "definitelyExcludedValue"
        mock_file_event_log_record.msg["unmappedFieldName"] = test_value
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        cef_parts = get_cef_parts(cef_out)
        del mock_file_event_log_record.msg["unmappedFieldName"]
        assert test_value not in cef_parts[-1]

    def test_format_includes_os_hostname_if_present(self, mock_file_event_log_record):
        expected_field_name = "shost"
        expected_value = "Test's MacBook Air"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_public_ip_address_if_present(
        self, mock_file_event_log_record
    ):
        expected_field_name = "src"
        expected_value = "71.34.4.22"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_user_uid_if_present(self, mock_file_event_log_record):
        expected_field_name = "suid"
        expected_value = "912338501981077099"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_device_username_if_present(
        self, mock_file_event_log_record
    ):
        expected_field_name = "suser"
        expected_value = "test.testerson+testair@code42.com"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_capacity_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cn1"
        expected_value = "5000000"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_capacity_label_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cn1Label"
        expected_value = "Code42AEDRemovableMediaCapacity"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_bus_type_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs1"
        expected_value = "TEST_BUS_TYPE"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_bus_type_label_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs1Label"
        expected_value = "Code42AEDRemovableMediaBusType"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_vendor_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs2"
        expected_value = "TEST_VENDOR_NAME"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_vendor_label_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs2Label"
        expected_value = "Code42AEDRemovableMediaVendor"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_name_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs3"
        expected_value = "TEST_NAME"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_name_label_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs3Label"
        expected_value = "Code42AEDRemovableMediaName"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_serial_number_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs4"
        expected_value = "TEST_SERIAL_NUMBER"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_removable_media_serial_number_label_if_present(
        self, mock_file_event_removable_media_event_log_record
    ):
        expected_field_name = "cs4Label"
        expected_value = "Code42AEDRemovableMediaSerialNumber"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_removable_media_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_actor_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "suser"
        expected_value = "actor@example.com"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_sync_destination_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "destinationServiceName"
        expected_value = "TEST_SYNC_DESTINATION"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_event_timestamp_if_present(
        self, mock_file_event_log_record
    ):
        expected_field_name = "end"
        expected_value = "1567996943851"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_create_timestamp_if_present(
        self, mock_file_event_log_record
    ):
        expected_field_name = "fileCreateTime"
        expected_value = "1342923569000"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_md5_checksum_if_present(self, mock_file_event_log_record):
        expected_field_name = "fileHash"
        expected_value = "19b92e63beb08c27ab4489fcfefbbe44"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_modify_timestamp_if_present(
        self, mock_file_event_log_record
    ):
        expected_field_name = "fileModificationTime"
        expected_value = "1355886008000"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_file_path_if_present(self, mock_file_event_log_record):
        expected_field_name = "filePath"
        expected_value = "/Users/testtesterson/Downloads/About Downloads.lpdf/Contents/Resources/English.lproj/"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_file_name_if_present(self, mock_file_event_log_record):
        expected_field_name = "fname"
        expected_value = "InfoPlist.strings"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_file_size_if_present(self, mock_file_event_log_record):
        expected_field_name = "fsize"
        expected_value = "86"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_file_category_if_present(self, mock_file_event_log_record):
        expected_field_name = "fileType"
        expected_value = "UNCATEGORIZED"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_exposure_if_present(self, mock_file_event_log_record):
        expected_field_name = "reason"
        expected_value = "ApplicationRead"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_url_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "filePath"
        expected_value = "https://www.example.com"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_insertion_timestamp_if_present(
        self, mock_file_event_log_record
    ):
        expected_field_name = "rt"
        expected_value = "1568069262724"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_process_name_if_present(self, mock_file_event_log_record):
        expected_field_name = "sproc"
        expected_value = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_event_id_if_present(self, mock_file_event_log_record):
        expected_field_name = "externalId"
        expected_value = "0_1d71796f-af5b-4231-9d8e-df6434da4663_912339407325443353_918253081700247636_16"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_device_uid_if_present(self, mock_file_event_log_record):
        expected_field_name = "deviceExternalId"
        expected_value = "912339407325443353"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_domain_name_if_present(self, mock_file_event_log_record):
        expected_field_name = "dvchost"
        expected_value = "192.168.0.3"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_source_if_present(self, mock_file_event_log_record):
        expected_field_name = "sourceServiceName"
        expected_value = "Endpoint"
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_cloud_drive_id_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "aid"
        expected_value = "TEST_CLOUD_DRIVE_ID"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_shared_with_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "duser"
        expected_value = "example1@example.com,example2@example.com"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_tab_url_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "request"
        expected_value = "TEST_TAB_URL"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_window_title_if_present(
        self, mock_file_event_cloud_activity_event_log_record
    ):
        expected_field_name = "requestClientApplication"
        expected_value = "TEST_WINDOW_TITLE"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_cloud_activity_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_email_recipients_if_present(
        self, mock_file_event_email_event_log_record
    ):
        expected_field_name = "duser"
        expected_value = "test.recipient1@example.com,test.recipient2@example.com"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_email_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_email_sender_if_present(
        self, mock_file_event_email_event_log_record
    ):
        expected_field_name = "suser"
        expected_value = "TEST_EMAIL_SENDER"
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_email_event_log_record
        )
        assert key_value_pair_in_cef_extension(
            expected_field_name, expected_value, cef_out
        )

    def test_format_includes_correct_event_name_and_signature_id_for_created(
        self, mock_file_event_log_record
    ):
        event_type = "CREATED"
        mock_file_event_log_record.msg["eventType"] = event_type
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert event_name_assigned_correct_signature_id(event_type, "C42200", cef_out)

    def test_format_includes_correct_event_name_and_signature_id_for_modified(
        self, mock_file_event_log_record
    ):
        event_type = "MODIFIED"
        mock_file_event_log_record.msg["eventType"] = event_type
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert event_name_assigned_correct_signature_id(event_type, "C42201", cef_out)

    def test_format_includes_correct_event_name_and_signature_id_for_deleted(
        self, mock_file_event_log_record
    ):
        event_type = "DELETED"
        mock_file_event_log_record.msg["eventType"] = event_type
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert event_name_assigned_correct_signature_id(event_type, "C42202", cef_out)

    def test_format_includes_correct_event_name_and_signature_id_for_read_by_app(
        self, mock_file_event_log_record
    ):
        event_type = "READ_BY_APP"
        mock_file_event_log_record.msg["eventType"] = event_type
        cef_out = FileEventDictToCEFFormatter().format(mock_file_event_log_record)
        assert event_name_assigned_correct_signature_id(event_type, "C42203", cef_out)

    def test_format_includes_correct_event_name_and_signature_id_for_emailed(
        self, mock_file_event_email_event_log_record
    ):
        event_type = "EMAILED"
        mock_file_event_email_event_log_record.msg["eventType"] = event_type
        cef_out = FileEventDictToCEFFormatter().format(
            mock_file_event_email_event_log_record
        )
        assert event_name_assigned_correct_signature_id(event_type, "C42204", cef_out)


class TestFileEventDictToJSONFormatter:
    def test_format_returns_expected_number_of_fields(self, mock_file_event_log_record):
        json_out = FileEventDictToJSONFormatter().format(mock_file_event_log_record)
        file_event_dict = json.loads(json_out)
        assert len(file_event_dict) == 25  # Fields that are not null or an empty list

    def test_format_returns_only_non_null_fields(self, mock_file_event_log_record):
        json_out = FileEventDictToJSONFormatter().format(mock_file_event_log_record)
        file_event_dict = json.loads(json_out)
        for key in file_event_dict:
            if not file_event_dict[key] and file_event_dict != 0:
                raise AssertionError()
        assert True


class TestFileEventDictToRawJSONFormatter:
    def test_format_returns_expected_number_of_fields(self, mock_file_event_log_record):
        json_out = FileEventDictToRawJSONFormatter().format(mock_file_event_log_record)
        file_event_dict = json.loads(json_out)
        assert len(file_event_dict) == 40

    def test_format_is_okay_with_null_values(self, mock_file_event_log_record):
        json_out = FileEventDictToRawJSONFormatter().format(mock_file_event_log_record)
        file_event_dict = json.loads(json_out)
        assert (
            file_event_dict["actor"] is None
        )  # actor happens to be null in this case.


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

    # `assert False` can cause test call to be removed, according to flake8.
    raise AssertionError()
