# Alert Rules

## add-user

Add a user to a given alert rule.

Arguments:
* `--rule-id`: Observer ID of the rule to be updated.
* `--username`, `-u` The username of the user to add to the alert rule.

Usage:
```bash
code42 alert-rules add-user --rule-id <rule-id> --username <username>
```

##  remove-user

Remove a user to a given alert rule.

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

Print out detailed alert rule criteria.

Arguments:
* `rule-id`: Observer ID of the rule.

Usage:
```bash
code42 alert-rules show <rule-id>
```

## bulk generate-template

Generate the necessary csv template for bulk actions.

Arguments:
* `cmd`: The type of command the template will be used for. Available choices= [add, remove].

Usage:
```bash
code42 alert-rules bulk generate-template <cmd>
```

## bulk add

Add users to alert rules. CSV file format: `rule_id,username`.

Arguments:
* `file-name`: The path to the csv file with columns 'rule_id,username'for bulk adding users to the alert rule.

Usage:
```bash
code42 alert-rules bulk add <filename>
```

## bulk remove

Remove users from alert rules. CSV file format: `rule_id,username`.

Arguments:
* `file-name`: The path to the csv file with columns 'rule_id,username' for bulk removing users to the alert rule.

Usage:
```bash
code42 alert-rules bulk remove <filename>
```
