from __future__ import print_function
import json
from datetime import datetime, timedelta

from c42secevents.common import FileEventHandlers
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import convert_datetime_to_timestamp
from py42.sdk import SDK

from c42sec._internal.logger_factory import get_error_logger
from c42sec.profile import get_profile


def extract_to_destination(output_logger, args):
    handlers = _create_event_handlers_for_logging_output(output_logger)
    profile = get_profile()
    code42 = SDK.create_using_local_account(profile.authority_url, profile.username, profile.get_password())
    min_timestamp = _parse_min_timestamp(args.begin_date) if args.begin_date else None
    max_timestamp = _parse_timestamp(args.end_date) if args.end_date else None
    AEDEventExtractor(code42, handlers).extract(initial_min_timestamp=min_timestamp, max_timestamp=max_timestamp)


def _create_event_handlers_for_logging_output(output_logger):
    handlers = FileEventHandlers()
    error_logger = get_error_logger()
    handlers.handle_error = error_logger.error

    def handle_response(response):
        response_dict = json.loads(response.text)
        events = response_dict.get(u"fileEvents")
        for event in events:
            output_logger.info(event)

    handlers.handle_response = handle_response
    return handlers


def _parse_min_timestamp(begin_date):
    min_timestamp = _parse_timestamp(begin_date)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        print("Argument '--begin' must be within 90 days.")
        exit(1)
    return min_timestamp


def _parse_timestamp(input_string):
    try:
        # Input represents date str like '2020-02-13'
        time = datetime.strptime(input_string, "%Y-%m-%d")
    except ValueError:
        # Input represents amount of seconds ago like '86400'
        if input_string and input_string.isdigit():
            now = datetime.utcnow()
            time = now - timedelta(minutes=int(input_string))
        else:
            raise ValueError("input must be a positive integer or a date in YYYY-MM-DD format.")

    return convert_datetime_to_timestamp(time)
