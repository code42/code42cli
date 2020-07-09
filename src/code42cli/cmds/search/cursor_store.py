import os
from os import path

from code42cli.errors import Code42CLIError
from code42cli.util import get_user_project_path


class Cursor(object):
    def __init__(self, location):
        self._location = location
        self._name = path.basename(location)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        with open(self._location) as checkpoint:
            return checkpoint.read()


class BaseCursorStore(object):
    def __init__(self, dir_path):
        self._dir_path = dir_path

    def get(self, cursor_name):
        """Gets the last stored date observed timestamp."""
        try:
            location = path.join(self._dir_path, cursor_name)
            with open(location) as checkpoint:
                return float(checkpoint.read())
        except FileNotFoundError:
            return None

    def replace(self, cursor_name, new_timestamp):
        """Replaces the last stored date observed timestamp with the given one."""
        location = path.join(self._dir_path, cursor_name)
        with open(location, "w") as checkpoint:
            return checkpoint.write(str(new_timestamp))

    def delete(self, cursor_name):
        """Removes a single cursor from the store."""
        try:
            location = path.join(self._dir_path, cursor_name)
            os.remove(location)
        except FileNotFoundError:
            msg = "No checkpoint named {0} exists for this profile.".format(cursor_name)
            raise Code42CLIError(msg)

    def clean(self):
        """Removes all cursors from this store."""
        cursors = self.get_all_cursors()
        for cursor in cursors:
            self.delete(cursor.name)

    def get_all_cursors(self):
        """Returns a list of all cursors stored in this directory (which istypically scoped to a profile)."""
        dir_contents = os.listdir(self._dir_path)
        return [Cursor(f) for f in dir_contents if self._is_file(f)]

    def _is_file(self, node_name):
        return path.isfile(path.join(self._dir_path, node_name))


class FileEventCursorStore(BaseCursorStore):
    def __init__(self, profile_name):
        dir_path = get_user_project_path(u"file_event_checkpoints", profile_name)
        super(FileEventCursorStore, self).__init__(dir_path)


class AlertCursorStore(BaseCursorStore):
    def __init__(self, profile_name):
        dir_path = get_user_project_path(u"alert_checkpoints", profile_name)
        super(AlertCursorStore, self).__init__(dir_path)


def get_file_event_cursor_store(profile_name):
    return FileEventCursorStore(profile_name)


def get_alert_cursor_store(profile_name):
    return AlertCursorStore(profile_name)


def get_all_cursor_stores_for_profile(profile_name):
    return [FileEventCursorStore(profile_name), AlertCursorStore(profile_name)]
