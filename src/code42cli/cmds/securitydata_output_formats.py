from datetime import datetime

from c42eventextractor.logging.formatters import CEF_TEMPLATE
from c42eventextractor.logging.formatters import CEF_TIMESTAMP_FIELDS
from c42eventextractor.maps import CEF_CUSTOM_FIELD_NAME_MAP
from c42eventextractor.maps import FILE_EVENT_TO_SIGNATURE_ID_MAP
from c42eventextractor.maps import JSON_TO_CEF_MAP

import code42cli.cmds.search.enums as enum
from code42cli.output_formats import CEF_DEFAULT_PRODUCT_NAME
from code42cli.output_formats import CEF_DEFAULT_SEVERITY_LEVEL
from code42cli.output_formats import OutputFormatter


class FileEventsOutputFormatter(OutputFormatter):
    def __init__(self, output_format, header=None):
        output_format = (
            output_format.upper()
            if output_format
            else enum.FileEventsOutputFormat.TABLE
        )
        super().__init__(output_format, header)
        if output_format == enum.FileEventsOutputFormat.CEF:
            self._format_func = to_cef


def to_cef(output):
    """Output is a single record"""
    return "{}\n".format(_convert_event_to_cef(output))


def _convert_event_to_cef(event):
    kvp_list = {
        JSON_TO_CEF_MAP[key]: event[key]
        for key in event
        if key in JSON_TO_CEF_MAP and (event[key] is not None and event[key] != [])
    }

    extension = " ".join(_format_cef_kvp(key, kvp_list[key]) for key in kvp_list)
    event_name = event.get("eventType", "UNKNOWN")
    signature_id = FILE_EVENT_TO_SIGNATURE_ID_MAP.get(event_name, "C42000")

    cef_log = CEF_TEMPLATE.format(
        productName=CEF_DEFAULT_PRODUCT_NAME,
        signatureID=signature_id,
        eventName=event_name,
        severity=CEF_DEFAULT_SEVERITY_LEVEL,
        extension=extension,
    )
    return cef_log


def _format_cef_kvp(cef_field_key, cef_field_value):
    if cef_field_key + "Label" in CEF_CUSTOM_FIELD_NAME_MAP:
        return _format_custom_cef_kvp(cef_field_key, cef_field_value)

    cef_field_value = _handle_nested_json_fields(cef_field_key, cef_field_value)
    if isinstance(cef_field_value, list):
        cef_field_value = _convert_list_to_csv(cef_field_value)
    elif cef_field_key in CEF_TIMESTAMP_FIELDS:
        cef_field_value = _convert_file_event_timestamp_to_cef_timestamp(
            cef_field_value
        )
    return "{}={}".format(cef_field_key, cef_field_value)


def _format_custom_cef_kvp(custom_cef_field_key, custom_cef_field_value):
    custom_cef_label_key = "{}Label".format(custom_cef_field_key)
    custom_cef_label_value = CEF_CUSTOM_FIELD_NAME_MAP[custom_cef_label_key]
    return "{}={} {}={}".format(
        custom_cef_field_key,
        custom_cef_field_value,
        custom_cef_label_key,
        custom_cef_label_value,
    )


def _handle_nested_json_fields(cef_field_key, cef_field_value):
    result = []
    if cef_field_key == "duser":
        result = [
            item["cloudUsername"] for item in cef_field_value if type(item) is dict
        ]

    return result or cef_field_value


def _convert_list_to_csv(_list):
    value = ",".join([val for val in _list])
    return value


def _convert_file_event_timestamp_to_cef_timestamp(timestamp_value):
    try:
        _datetime = datetime.strptime(timestamp_value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        _datetime = datetime.strptime(timestamp_value, "%Y-%m-%dT%H:%M:%SZ")
    value = "{:.0f}".format(_datetime_to_ms_since_epoch(_datetime))
    return value


def _datetime_to_ms_since_epoch(_datetime):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds = (_datetime - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return total_seconds * 1000
