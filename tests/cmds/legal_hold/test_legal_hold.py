import pytest

from code42cli.cmds.legal_hold import add_user, add_bulk_users, remove_user, remove_bulk_users
from py42.exceptions import Py42BadRequestError
