# Associate Users to Alert Rules

Once you [create an alert rule in the Code42 console](https://support.code42.com/Administrator/Cloud/Code42_console_reference/Alert_rule_settings_reference), you can use the CLI `alert-rules` commands to add and remove users from your existing alert rules.

To see a list of all the users currently in your organization: 
- Export a list from the [Users action menu](https://support.code42.com/Administrator/Cloud/Code42_console_reference/Users_reference#Action_menu).
- Use the [CLI users commands](./users.md) to print all users.

## View Existing Alert Rules

You'll need the ID of an alert rule to add or remove a user.

To view a list of all alert rules currently created for your organization, including the rule ID, use the following command:
```bash
code42 alert-rules list
```

If you've identified the rule ID, to view the details of that alert rule use:
```bash
code42 alert-rules show <rule-ID>
```

#### Example output
Example output for a single alert rule in default JSON format.
```json
{
    "type$": "ENDPOINT_EXFILTRATION_RULE_DETAILS_RESPONSE",
    "rules": [
        {
            "type$": "ENDPOINT_EXFILTRATION_RULE_DETAILS",
            "tenantId": "c4e43418-07d9-4a9f-a138-29f39a124d33",
            "name": "My Rule",
            "description": "this is your rule!",
            "severity": "HIGH",
            "isEnabled": false,
            "fileBelongsTo": {
                "type$": "FILE_BELONGS_TO",
                "usersToAlertOn": "ALL_USERS"
            },
            "notificationConfig": {
                "type$": "NOTIFICATION_CONFIG",
                "enabled": false
            },
            "fileCategoryWatch": {
                "type$": "FILE_CATEGORY_WATCH",
                "watchAllFiles": true
            },
            "ruleSource": "Alerting",
            "fileSizeAndCount": {
                "type$": "FILE_SIZE_AND_COUNT",
                "fileCountGreaterThan": 2,
                "totalSizeGreaterThanInBytes": 200,
                "operator": "AND"
            },
            "fileActivityIs": {
                "type$": "FILE_ACTIVITY",
                "syncedToCloudService": {
                    "type$": "SYNCED_TO_CLOUD_SERVICE",
                    "watchBox": false,
                    "watchBoxDrive": false,
                    "watchDropBox": false,
                    "watchGoogleBackupAndSync": false,
                    "watchAppleIcLoud": false,
                    "watchMicrosoftOneDrive": false
                },
                "uploadedOnRemovableMedia": true,
                "readByBrowserOrOther": true
            },
            "timeWindow": 15,
            "id": "404ff012-fa2f-4acf-ae6d-107eabf7f24c",
            "createdAt": "2021-04-27T01:55:36.4204590Z",
            "createdBy": "sean.cassidy@example.com",
            "modifiedAt": "2021-09-03T01:46:13.2902310Z",
            "modifiedBy": "sean.cassidy@example.com",
            "isSystem": false
        }
    ]
}
```

## Add a User to an Alert Rule

You can manage the users who are associated with an alert rule once you know the rule's `rule_id` and the user's `username`.

To add a single user to your alert rule, use the following command.
```bash
code42 alert-rules add-user --rule-id <rule-id> -u sean.cassidy@example.com
```

Alternatively, to add multiple users to your alert rule, fill out the `add` CSV file template, then use the `bulk add` command with the CSV file path.
```bash
code42 alert-rules bulk add users.csv
```

You can remove single or multiple users from alert rules similarly using the `remove-user` and `bulk remove` commands.


## Get CSV Template

The following command will generate a CSV template to either add or remove users from multiple alert rules at once.  The CSV file will be saved to the current working directory.
```bash
code42 alert-rules bulk generate-template [add|remove]
```

Each of the CSV templates can then be filled out and used with their respective bulk command.
```bash
code42 alert-rules bulk [add|remove] Users/my_user/bulk-command.csv
```

For example, to associate one or more users to one or more alert rules:

1. Generate a CSV template. Below is the command for generating a template to add users to an alert rules. Once generated, the CSV file is saved to your current working directory.

```bash
code42 alert-rules bulk generate-template add
```

2. Use the CSV template to enter each trusted activity's information.
   The `rule_id` and `username` fields are required. The `rule_id` refers to the ID number of the alert rule to add the users too, and the `username` refers to that of the user to add to the alert rule.

3. Save the CSV file.

Learn more about the [Alert Rules](../commands/alertrules.md) commands.
