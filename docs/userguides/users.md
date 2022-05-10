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

#### View User Roles
View a user's current roles and other details with the `show` command:
```bash
code42 users show "sean.cassidy@example.com"
```
Alternatively, pass the `--include-roles` flag to the `list ` command.  The following command will print a list of all active users and their current roles:
```bash
code42 users list --active --include-roles
```

#### Update User Roles

Use the following command to add a role to a user:
```bash
code42 users add-role --username "sean.cassidy@example.com" --role-name "Desktop User"
```

Similarly, use the `remove-role` command to remove a role from a user.

## Manage User Risk Profile info

To set a start or end/departure date on a User's profile (useful for users on the "New Hire" and "Departing" Watchlists):

```bash
code42 users update-start-date 2020-03-10 user@example.com

code42 users update-departure-date 2022-06-20 user@example.com
```

To clear the value of start_date/end_date on a User's profile, use the `--clear` option to the above commands:

```bash
code42 users update-departure-date --clear user@example.com
```

To update a User's Risk Profile notes field:

```bash
code42 users update-risk-profile-notes user@example.com "New note text"
```

By default, the note text will overwrite notes are already on the profile. To keep existing note data, use the `--append` option:

```bash
code42 users update-risk-profile-notes user@example.com "Additional note text" --append
```

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

You'll need an organization's unique identifier number (UID) to move a user into it.  You can use the `list` command to view a list of all current user organizations, including UIDs:
```bash
code42 users orgs list
```

Use the `show` command to view all the details of a user organization.
As an example, to print the details of an organization associated with the UID `123456789` in JSON format:
```bash
code42 users show 123456789 -f JSON
```

Once you've identified your organizations UID number, use the `move` command to move a user into that organization.  In the following example a user is moved into the organization associated with the UID `1234567890`:
```bash
code42 users move --username sean.cassidy@example.com --org-id 1234567890
```

Alternatively, to move multiple users between organizations, fill out the `move` CSV file template, then use the `bulk move` command with the CSV file path.
```bash
code42 users bulk move bulk-command.csv
```

## Get CSV Template for bulk commands

The following command generates a CSV template for each of the available bulk user commands.  The CSV file is saved to the current working directory.
```bash
code42 users bulk generate-template [update|move|add-alias|remove-alias|update-risk-profile]
```

Once generated, fill out and use each of the CSV templates with their respective bulk commands.
```bash
code42 users bulk [update|move|deactivate|reactivate|add-alias|remove-alias|update-risk-profile] bulk-command.csv
```

A CSV with a `username` column and a single username on each new line is used for the `reactivate` and `deactivate` bulk commands.  These commands are not available as options for `generate-template`.

Learn more about [Managing Users](../commands/users.md).
