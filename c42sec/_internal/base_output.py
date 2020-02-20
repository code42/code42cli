import json
from c42secevents.common import FileEventHandlers
from c42secevents.extractors import AEDEventExtractor
from py42.sdk import SDK

from c42sec._internal.logger_factory import get_error_logger
from c42sec.profile import get_profile


def output_to_destination(output_logger):
    handlers = _create_event_handlers_for_logging_output(output_logger)
    profile = get_profile()
    code42 = SDK.create_using_local_account(profile.authority_url, profile.username, profile.get_password())
    AEDEventExtractor(code42, handlers).extract()


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
