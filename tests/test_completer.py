from code42cli.completer import Completer


class TestCompleter(object):
    _completer = Completer()
    
    def test_complete_main_returns_empty_list(self):
        actual = self._completer.complete("code42")
        assert [] == actual

    def test_complete_for_profile(self):
        actual = self._completer.complete("code42 profi")
        assert "profile" in actual

    def test_complete_for_security_data(self):
        actual = self._completer.complete("code42 security")
        assert "security-data" in actual

    def test_complete_for_alert_and_rules(self):
        actual = self._completer.complete("code42 al")
        assert "alerts" in actual
        assert "alert-rules" in actual

    def test_complete_for_departing_employee(self):
        actual = self._completer.complete("code42 de")
        assert "departing-employee" in actual

    def test_complete_for_high_risk_employee(self):
        actual = self._completer.complete("code42 hi")
        assert "high-risk-employee" in actual

    def test_complete_for_high_risk_employee_bulk(self):
        actual = self._completer.complete("code42 high-risk-employee bu")
        assert "bulk" in actual

    def test_complete_for_departing_employee_bulk(self):
        actual = self._completer.complete("code42 departing-employee bu")
        assert "bulk" in actual

    def test_complete_for_alert_rules_bulk(self):
        actual = self._completer.complete("code42 alert-rules b")
        assert "bulk" in actual

    def test_complete_for_high_risk_employee_bulk_gen_template(self):
        actual = self._completer.complete("code42 high-risk-employee bulk gen")
        assert "generate-template" in actual

    def test_complete_for_departing_employee_bulk_gen_template(self):
        actual = self._completer.complete("code42 departing-employee bulk generate-")
        assert "generate-template" in actual

    def test_complete_for_alert_rules_bulk_gen_template(self):
        actual = self._completer.complete("code42 alert-rules bulk gen")
        assert "generate-template" in actual
