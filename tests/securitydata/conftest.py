import pytest

from tests.conftest import get_test_date_str

SECURITYDATA_NAMESPACE = "code42cli.securitydata"
SUBCOMMANDS_NAMESPACE = "{0}.subcommands".format(SECURITYDATA_NAMESPACE)


begin_date_tuple = (get_test_date_str(days_ago=89),)
begin_date_tuple_with_time = (get_test_date_str(days_ago=89), "3:12:33")
end_date_tuple = (get_test_date_str(days_ago=10),)
end_date_tuple_with_time = (get_test_date_str(days_ago=10), "11:22:43")


@pytest.fixture(autouse=True)
def sqlite_connection(mocker):
    return mocker.patch("sqlite3.connect")
