from datetime import datetime, timedelta


def parse_timestamp(input_string):
    try:
        time = datetime.strptime(input_string, "%Y-%m-%d")
    except ValueError:
        if input_string and input_string.isdigit():
            now = datetime.utcnow()
            time = now - timedelta(minutes=int(input_string))
        else:
            raise ValueError("input must be a positive integer or a date in YYYY-MM-DD format.")

    return convert_date_to_timestamp(time)


def convert_date_to_timestamp(date):
    return (date - datetime.utcfromtimestamp(0)).total_seconds()
