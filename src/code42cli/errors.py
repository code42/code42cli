from click import ClickException
from code42cli.logger import get_view_exceptions_location_message

ERRORED = False


class LoggedCLIError(ClickException):
    def __init(self, message=None):
        self.message = message

    def format_message(self):
        locations_message = get_view_exceptions_location_message()
        return (
            u"{}\n{}".format(self.message, locations_message) if self.message else locations_message
        )


class UserAlreadyAddedError(ClickException):
    def __init__(self, username, list_name):
        msg = u"'{}' is already on the {}.".format(username, list_name)
        super().__init__(msg)


class UnknownRiskTagError(ClickException):
    def __init__(self, bad_tags):
        tags = u", ".join(bad_tags)
        super().__init__(u"The following risk tags are unknown: '{}'.".format(tags))


class InvalidRuleTypeError(ClickException):
    def __init__(self, rule_id, source):
        msg = u"Only alert rules with a source of 'Alerting' can be targeted by this command. "
        msg += "Rule {0} has a source of '{1}'."
        super().__init__(msg.format(rule_id, source))


class UserDoesNotExistError(ClickException):
    """An error to represent a username that is not in our system. The CLI shows this error when 
    the user tries to add or remove a user that does not exist. This error is not shown during 
    bulk add or remove."""

    def __init__(self, username):
        super().__init__(u"User '{}' does not exist.".format(username))


class UserNotInLegalHoldError(ClickException):
    def __init__(self, username, matter_id):
        super().__init__(
            u"User '{}' is not an active member of legal hold matter '{}'".format(
                username, matter_id
            )
        )


class LegalHoldNotFoundOrPermissionDeniedError(ClickException):
    def __init__(self, matter_id):
        super().__init__(
            u"Matter with id={} either does not exist or your profile does not have permission to "
            u"view it.".format(matter_id)
        )
