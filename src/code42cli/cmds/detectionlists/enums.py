class DetectionLists(object):
    DEPARTING_EMPLOYEE = u"departing-employee"
    HIGH_RISK_EMPLOYEE = u"high-risk-employee"


class DetectionListUserKeys(object):
    CLOUD_ALIAS = u"cloud_alias"
    USERNAME = u"username"
    NOTES = u"notes"
    RISK_TAG = u"risk_tag"


class RiskTags(object):
    FLIGHT_RISK = u"FLIGHT_RISK"
    HIGH_IMPACT_EMPLOYEE = u"HIGH_IMPACT_EMPLOYEE"
    ELEVATED_ACCESS_PRIVILEGES = u"ELEVATED_ACCESS_PRIVILEGES"
    PERFORMANCE_CONCERNS = u"PERFORMANCE_CONCERNS"
    SUSPICIOUS_SYSTEM_ACTIVITY = u"SUSPICIOUS_SYSTEM_ACTIVITY"
    POOR_SECURITY_PRACTICES = u"POOR_SECURITY_PRACTICES"
    CONTRACT_EMPLOYEE = u"CONTRACT_EMPLOYEE"

    def __iter__(self):
        return iter(
            [
                self.FLIGHT_RISK,
                self.HIGH_IMPACT_EMPLOYEE,
                self.ELEVATED_ACCESS_PRIVILEGES,
                self.PERFORMANCE_CONCERNS,
                self.SUSPICIOUS_SYSTEM_ACTIVITY,
                self.POOR_SECURITY_PRACTICES,
                self.CONTRACT_EMPLOYEE,
            ]
        )
