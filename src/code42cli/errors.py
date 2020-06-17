from click import BadOptionUsage

ERRORED = False


class BadFileError(Exception):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        super(BadFileError, self).__init__()


class EmptyFileError(BadFileError):
    def __init__(self, file_path):
        super(EmptyFileError, self).__init__(file_path, u"Given empty file {}.".format(file_path))


class Code42CLIError(Exception):
    pass


class UserAlreadyAddedError(Code42CLIError):
    def __init__(self, username, list_name):
        msg = u"'{}' is already on the {}.".format(username, list_name)
        super(UserAlreadyAddedError, self).__init__(msg)


class UnknownRiskTagError(Code42CLIError):
    def __init__(self, bad_tags):
        tags = u", ".join(bad_tags)
        super(UnknownRiskTagError, self).__init__(
            u"The following risk tags are unknown: '{}'.".format(tags)
        )


class InvalidRuleTypeError(Code42CLIError):
    def __init__(self, rule_id, source):
        msg = u"Only alert rules with a source of 'Alerting' can be targeted by this command. "
        msg += "Rule {0} has a source of '{1}'."
        super(InvalidRuleTypeError, self).__init__(msg.format(rule_id, source))


class UserDoesNotExistError(Code42CLIError):
    """An error to represent a username that is not in our system. The CLI shows this error when 
    the user tries to add or remove a user that does not exist. This error is not shown during 
    bulk add or remove."""

    def __init__(self, username):
        super(UserDoesNotExistError, self).__init__(u"User '{}' does not exist.".format(username))


class UserNotInLegalHoldError(Code42CLIError):
    def __init__(self, username, matter_id):
        super(UserNotInLegalHoldError, self).__init__(
            u"User '{}' is not an active member of legal hold matter '{}'".format(
                username, matter_id
            )
        )


class LegalHoldNotFoundOrPermissionDeniedError(Code42CLIError):
    def __init__(self, matter_id):
        super(LegalHoldNotFoundOrPermissionDeniedError, self).__init__(
            u"Matter with id={} either does not exist or your profile does not have permission to "
            u"view it.".format(matter_id)
        )


class DateArgumentError(BadOptionUsage):
    def __init__(self, option_name=None, message=None):
        if option_name:
            message = "--{} {}".format(option_name, message)
        super(DateArgumentError, self).__init__(option_name, message)
