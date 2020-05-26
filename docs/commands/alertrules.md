# Alert Rules

## add-user

Update alert rule criteria to monitor users against the given username.

Arguments:
* `--rule-id`: Observer ID of the rule to be updated.
* `--username`, `-u` The username of the user to add to the alert rule.

Usage:
```bash
code42 alert-rules add-user --rule-id <rule-id> --username <username>
```

##  remove-user

Update alert rule criteria to remove a user.

Arguments:
* `--rule-id`: Observer ID of the rule to be updated.
* `--username`, `-u`: The username of the user to remove from the alert rule.

Usage:
```bash
code42 alert-rules remove-user --rule-id <rule-id> --username <username>
```

## list

Fetch existing alert rules.

Usage:
```bash
code42 alert-rules list
```

## show

Fetch configured alert-rules against the rule ID.

Arguments:
* `rule-id`: Observer ID of the rule.

Usage:
```bash
code42 alert-rules show <rule-id>
```

## bulk generate-template

Generate the necessary csv template for bulk actions.

Arguments:
* `cmd`: The type of command the template with be used for. Available choices= [add, remove].

Usage:
```bash
code42 alert-rules bulk generate-template <cmd>
```

## bulk add

Update alert rule criteria to add users. CSV file format: `rule_id,username`.

Arguments:
* `file-name`: The path to the csv file with columns 'rule_id,username'for bulk adding users to the alert rule.

Usage:
```bash
code42 alert-rules bulk add <filename>
```

## bulk remove

Update alert rule criteria to remove users. CSV file format: `rule_id,username`.

Arguments:
* `file-name`: The path to the csv file with columns 'rule_id,username' for bulk removing users to the alert rule.

Usage:
```bash
code42 alert-rules bulk remove <filename>
```
