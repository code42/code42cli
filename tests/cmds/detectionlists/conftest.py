import pytest


TEST_ID = "TEST_ID"


@pytest.fixture
def sdk_with_user(sdk):
    sdk.users.get_by_username.return_value = {"users": [{"userUid": TEST_ID}]}
    return sdk


@pytest.fixture
def sdk_without_user(sdk):
    sdk.users.get_by_username.return_value = {"users": []}
    return sdk
