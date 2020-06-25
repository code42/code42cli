from code42cli.errors import UserDoesNotExistError


def get_user_id(sdk, username):
    """Returns the user's UID (referred to by `user_id` in detection lists). Raises 
    `UserDoesNotExistError` if the user doesn't exist in the Code42 server.
    
    Args:
        sdk (py42.sdk.SDKClient): The py42 sdk.
        username (str or unicode): The username of the user to get an ID for.
    
    Returns:
         str: The user ID for the user with the given username.
    """
    users = sdk.users.get_by_username(username)[u"users"]
    if not users:
        raise UserDoesNotExistError(username)
    return users[0][u"userUid"]
