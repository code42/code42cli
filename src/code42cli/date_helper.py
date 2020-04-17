def parse_min_timestamp(begin_date_str):
    min_time = _parse_timestamp(begin_date_str)
    min_timestamp = convert_datetime_to_timestamp(min_time)
    boundary_date = datetime.utcnow() - timedelta(days=_MAX_LOOK_BACK_DAYS)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        raise ValueError(u"'Begin date' must be within 90 days.")
    return min_timestamp
