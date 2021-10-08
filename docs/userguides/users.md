# Manage Users

You can use the CLI to manage user information, update user roles, and move users between organizations.

To view a all the users currently in your organization, you can export a list from the [Users list in the Code42 console](https://support.code42.com/Administrator/Cloud/Code42_console_reference/Users_reference) or you can use the `list` command.

You can use optional flags to filter the users you want to view. The following command will print all active users with the `Desktop User` role who belong to the organization with UID `1234567890`:
```bash
code42 users list --org-uid 1234567890 --role-name "Desktop User" --active
```

To change the information for one or more users, provide the user UID and updated information with the `update` or `bulk update` commands.

## Manage User Roles

Apply [Code42's user roles](https://support.code42.com/Administrator/Cloud/Monitoring_and_managing/Roles_resources/Roles_reference#Standard_roles) to user accounts to provide administrators with the desired set of permissions.  Each role has associated permissions, limitations, and recommended use cases.

Use the following command to add a role to a user:
```bash
code42 users add-role --username "sean.cassidy@example.com" --role-name "Desktop User"
```

Similarly, use the `remove-role` command to remove a role from a user.

## Deactivate a User

You can deactivate a user with the following command:
```bash
code42 users deactivate sean.cassidy@example.com
```

To deactivate multiple users at once, enter each username on a new line in a CSV file, then use the `bulk deactivate` command with the CSV file path. For example:
```bash
code42 users bulk deactivate users_to_deactivate.csv
```

Similarly, use the `reactivate` and `bulk reactivate` commands to reactivate a user.

## Assign an Organization

Use [Organizations](https://support.code42.com/Administrator/Cloud/Code42_console_reference/Organizations_reference) to group users together in the Code42 environment.

Use the following example command to move a user into an organization associated with the `org_id` 1234567890:
```bash
code42 users move --username sean.cassidy@example.com --org-id 1234567890
```

Alternatively, to move multiple users between organizations, fill out the `move` CSV file template, then use the `bulk move` command with the CSV file path.
```bash
code42 users bulk move bulk-command.csv
```

## Get CSV Template

The following command generates a CSV template to either update users' data, or move users between organizations.  The csv file is saved to the current working directory.
```bash
code42 trusted-activities bulk generate-template [update|move]
```

Once generated, fill out and use each of the CSV templates with their respective bulk commands.
```bash
code42 trusted-activities bulk [update|move|reactivate|deactivate] bulk-command.csv
```
A CSV with a `username` column and a single username on each new line is used for the `reactivate` and `deactivate` bulk commands.  These commands are not available as options for `generate-template`.

Learn more about [Managing Users](../commands/users.md).
