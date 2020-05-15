# run the help commands on some stuff to prove stuff loads
from code42cli.main import main


def _execute_test(capsys, assert_command, assert_value=False):
    try:
        main()
    except SystemExit:
        assert_value = True
        capture = capsys.readouterr()
        assert assert_command in capture.out
    assert assert_value


def test_securitydata_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"security-data", u"print", u"-h"])
    _execute_test(capsys, u"print")


def test_alerts_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"alerts", u"print", u"-h"])
    _execute_test(capsys, u"print")


def test_profile_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"profile", u"show", u"-h"])
    _execute_test(capsys, u"show")


def test_departing_employee_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"departing-employee", u"add", u"-h"])
    _execute_test(capsys, u"add")


def test_high_risk_employee_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"high-risk-employee", u"bulk", u"-h"])
    _execute_test(capsys, u"bulk")


def test_alert_rules_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"alert-rules", u"bulk", u"add", u"-h"])
    _execute_test(capsys, u"add")
