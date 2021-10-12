import json
import os
from os import path

from code42cli.errors import Code42CLIError
from code42cli.util import get_user_project_path


class Cursor:
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


class BaseCursorStore:
    def __init__(self, dir_path):
        self._dir_path = dir_path

    def get(self, cursor_name):
        """Gets the last stored date observed timestamp."""
        try:
            location = path.join(self._dir_path, cursor_name)
            with open(location) as checkpoint:
                checkpoint_value = checkpoint.read()
                if not checkpoint_value:
                    return None
                try:
                    return float(checkpoint_value)
                except ValueError:
                    raise Code42CLIError(
                        f"Unable to parse checkpoint from {location}, expected a unix-epoch timestamp, got '{checkpoint_value}'."
                    )
        except FileNotFoundError:
            return None

    def replace(self, cursor_name, new_checkpoint):
        """Replaces the last stored date observed timestamp with the given one."""
        location = path.join(self._dir_path, cursor_name)
        with open(location, "w") as checkpoint:
            checkpoint.write(str(new_checkpoint))

    def delete(self, cursor_name):
        """Removes a single cursor from the store."""
        try:
            location = path.join(self._dir_path, cursor_name)
            os.remove(location)
        except FileNotFoundError:
            msg = f"No checkpoint named {cursor_name} exists for this profile."
            raise Code42CLIError(msg)

    def clean(self):
        """Removes all cursors from this store."""
        cursors = self.get_all_cursors()
        for cursor in cursors:
            self.delete(cursor.name)

    def get_all_cursors(self):
        """Returns a list of all cursors stored in this directory (which is typically scoped to a profile)."""
        dir_contents = os.listdir(self._dir_path)
        return [Cursor(f) for f in dir_contents if self._is_file(f)]

    def _is_file(self, node_name):
        return path.isfile(path.join(self._dir_path, node_name))


class FileEventCursorStore(BaseCursorStore):
    def __init__(self, profile_name):
        dir_path = get_user_project_path("file_event_checkpoints", profile_name)
        super().__init__(dir_path)

    def get(self, cursor_name):
        """Gets the last stored date observed timestamp."""
        try:
            location = path.join(self._dir_path, cursor_name)
            with open(location) as checkpoint:
                checkpoint_value = checkpoint.read()
                if not checkpoint_value:
                    return None
                return str(checkpoint_value)
        except FileNotFoundError:
            return None


class AlertCursorStore(BaseCursorStore):
    def __init__(self, profile_name):
        dir_path = get_user_project_path("alert_checkpoints", profile_name)
        super().__init__(dir_path)

    def get_alerts(self, cursor_name):
        try:
            location = path.join(self._dir_path, cursor_name) + "_alerts"
            with open(location) as checkpoint:
                try:
                    return json.loads(checkpoint.read())
                except json.JSONDecodeError:
                    return []
        except FileNotFoundError:
            return []

    def replace_alerts(self, cursor_name, new_alerts):
        location = path.join(self._dir_path, cursor_name) + "_alerts"
        with open(location, "w") as checkpoint:
            checkpoint.write(json.dumps(new_alerts))


class AuditLogCursorStore(BaseCursorStore):
    def __init__(self, profile_name):
        dir_path = get_user_project_path("audit_log_checkpoints", profile_name)
        super().__init__(dir_path)

    def get_events(self, cursor_name):
        try:
            location = path.join(self._dir_path, cursor_name) + "_events"
            with open(location) as checkpoint:
                try:
                    return json.loads(checkpoint.read())
                except json.JSONDecodeError:
                    return []
        except FileNotFoundError:
            return []

    def replace_events(self, cursor_name, new_events):
        location = path.join(self._dir_path, cursor_name) + "_events"
        with open(location, "w") as checkpoint:
            checkpoint.write(json.dumps(new_events))


def get_all_cursor_stores_for_profile(profile_name):
    return [
        FileEventCursorStore(profile_name),
        AlertCursorStore(profile_name),
        AuditLogCursorStore(profile_name),
    ]
