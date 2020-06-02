import pytest
from requests import Response, HTTPError

from py42.exceptions import Py42BadRequestError


@pytest.fixture
def bad_request_for_user_already_added(mocker):
    resp = mocker.MagicMock(spec=Response)
    resp.text = "User already on list"
    return _create_bad_request_mock(resp)


@pytest.fixture
def generic_bad_request(mocker):
    resp = mocker.MagicMock(spec=Response)
    resp.text = "TEST"
    return _create_bad_request_mock(resp)


def _create_bad_request_mock(resp):
    base_err = HTTPError()
    base_err.response = resp
    return Py42BadRequestError(base_err)
