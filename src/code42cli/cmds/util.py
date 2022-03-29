import itertools

from py42.sdk.queries.alerts.filters import DateObserved
from py42.sdk.queries.fileevents.filters import EventTimestamp
from py42.sdk.queries.fileevents.filters import ExposureType
from py42.sdk.queries.fileevents.filters import InsertionTimestamp
from py42.sdk.queries.query_filter import FilterGroup
from py42.sdk.queries.query_filter import QueryFilterTimestampField

from code42cli import errors
from code42cli.date_helper import verify_timestamp_order
from code42cli.logger import get_main_cli_logger
from code42cli.output_formats import OutputFormat

logger = get_main_cli_logger()


def convert_to_or_query(filter_groups):
    and_group = FilterGroup([], "AND")
    or_group = FilterGroup([], "OR")
    filters = itertools.chain.from_iterable([f.filter_list for f in filter_groups])
    for _filter in filters:
        if _is_exempt_filter(_filter):
            and_group.filter_list.append(_filter)
        else:
            or_group.filter_list.append(_filter)
    if and_group.filter_list:
        return [and_group, or_group]
    else:
        return [or_group]


def _is_exempt_filter(f):
    # exclude timestamp filters by default from "OR" queries
    # if other filters need to be exempt when building a query, append them to this list
    # can either be a `QueryFilter` subclass, or a composed `FilterGroup` if more precision on
    # is needed for which filters should be "AND"ed
    or_query_exempt_filters = [
        InsertionTimestamp,
        EventTimestamp,
        DateObserved,
        ExposureType.exists(),
    ]

    for exempt in or_query_exempt_filters:
        if isinstance(exempt, FilterGroup):
            if f in exempt:
                return True
            else:
                continue
        elif f.term == exempt._term:
            return True
    return False


def try_get_default_header(include_all, default_header, output_format):
    """Returns appropriate header based on include-all and output format. If returns None,
    the CLI format option will figure out the header based on the data keys."""
    output_header = None if include_all else default_header
    if output_format != OutputFormat.TABLE and include_all:
        err_text = "--include-all only allowed for Table output format."
        logger.log_error(err_text)
        raise errors.Code42CLIError(err_text)
    return output_header


def create_time_range_filter(filter_cls, begin_date=None, end_date=None):
    """Creates a filter using the given filter class (must be a subclass of
    :class:`py42.sdk.queries.query_filter.QueryFilterTimestampField`) and date args. Returns
    `None` if both begin_date and end_date args are `None`.

    Args:
        filter_cls: The class of filter to create. (must be a subclass of
          :class:`py42.sdk.queries.query_filter.QueryFilterTimestampField`)
        begin_date: The begin date for the range.
        end_date: The end date for the range.
    """
    if not issubclass(filter_cls, QueryFilterTimestampField):
        raise Exception("filter_cls must be a subclass of QueryFilterTimestampField")

    if begin_date and end_date:
        verify_timestamp_order(begin_date, end_date)
        return filter_cls.in_range(begin_date, end_date)

    elif begin_date and not end_date:
        return filter_cls.on_or_after(begin_date)

    elif end_date and not begin_date:
        return filter_cls.on_or_before(end_date)
