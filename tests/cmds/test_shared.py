import pytest

from code42cli.cmds.shared import get_user_id
from code42cli.errors import UserDoesNotExistError


def test_get_user_id_when_user_does_not_raise_error(sdk_without_user):
    with pytest.raises(UserDoesNotExistError):
        get_user_id(sdk_without_user, "risky employee")
