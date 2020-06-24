from code42cli.main import main, MainSubcommandLoader


class TestMainSubcommandLoader(object):
    def test_getitem_returns_top_level_subcommand_names(self):
        loader = MainSubcommandLoader()
        assert "alerts" in loader.names
        assert "alert-rules" in loader.names
        assert "departing-employee" in loader.names

    def test_getitem_when_at_alert_level_returns_alerts_subcommand_names(self):
        loader = MainSubcommandLoader()
        subloader = loader[loader.ALERTS].names
        assert "print" in subloader
        assert "write-to" in subloader
        assert "clear-checkpoint" in subloader

    def test_getitem_returns_flagged_arg_names_when_is_leaf_command(self):
        loader = MainSubcommandLoader()
        args = loader[loader.ALERTS][u"print"]
        assert "--use-checkpoint" in args
        assert "--actor" in args

    def test_getitem_returns_choices_when_is_choice_based_arg(self):
        loader = MainSubcommandLoader()
        args = loader[loader.SECURITY_DATA][u"send-to"][u"127.0.0.1"]["-p"]
        assert "UDP" in args


# run the help commands on some stuff to prove stuff loads


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


def test_legal_hold_commands_load(capsys, mocker):
    mocker.patch("sys.argv", [u"code42", u"legal-hold", u"bulk", u"add", u"-h"])
    _execute_test(capsys, u"bulk")
