from click import ClickException

ERRORED = False


class Code42CLIError(Exception):
    pass


class BadFileError(Exception):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        super().__init__()


class EmptyFileError(BadFileError):
    def __init__(self, file_path):
        super().__init__(file_path, u"Given empty file {}.".format(file_path))


class UserAlreadyAddedError(Code42CLIError):
    def __init__(self, username, list_name):
        msg = u"'{}' is already on the {}.".format(username, list_name)
        super().__init__(msg)


class UnknownRiskTagError(Code42CLIError):
    def __init__(self, bad_tags):
        tags = u", ".join(bad_tags)
        super().__init__(u"The following risk tags are unknown: '{}'.".format(tags))


class InvalidRuleTypeError(Code42CLIError):
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


class UserNotInLegalHoldError(Code42CLIError):
    def __init__(self, username, matter_id):
        super().__init__(
            u"User '{}' is not an active member of legal hold matter '{}'".format(
                username, matter_id
            )
        )


class LegalHoldNotFoundOrPermissionDeniedError(Code42CLIError):
    def __init__(self, matter_id):
        super().__init__(
            u"Matter with id={} either does not exist or your profile does not have permission to "
            u"view it.".format(matter_id)
        )
