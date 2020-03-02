from py42.sdk.file_event_query.device_query import DeviceUsername


def create_c42_username_filter(username):
    return DeviceUsername.eq(username)
