# Configure Trusted Activities

You can add trusted activities to your organization to prevent file activity associated with these locations from appearing in your security event dashboards, user profiles, and alerts.

## Get CSV Template

The following command generates a CSV template to either create, update, or remove multiple trusted activities at once.  The CSV file is saved to the current working directory.
```bash
code42 trusted-activities bulk generate-template [create|update|remove]
```

You can then fill out and use each of the CSV templates with their respective bulk commands.
```bash
code42 trusted-activities bulk [create|update|remove] bulk-command.csv
```

## Add a New Trusted Activity

Use the `create` command to add a new trusted domain or Slack workspace to your organization's trusted activities.
```bash
code42 trusted-activities create DOMAIN mydomain.com --description "a new trusted activity"
```

To add multiple trusted activities at once, enter information about the trusted activity into the `create` CSV file template.
For each activity, the `type` and `value` fields are required.

   `type` indicates the category of activity:
   - `DOMAIN` indicates a trusted domain
   - `SLACK` indicates a trusted Slack workspace

   `value` indicates either the name of the domain or Slack workspace.

Then use the `bulk create` command with the CSV file path. For example:
```bash
code42 trusted-activities bulk create create_trusted_activities.csv
```

## Update a Trusted Activity

Use the `update` command to update either the value or description of a single trusted activity. The `resource_id` of the activity is required.  The other fields are optional.

```bash
code42 trusted-activities update 123 --value my-updated-domain.com --description "an updated trusted activity"
```

To update multiple trusted activities at once, enter information about the trusted activity into the `update` CSV file template, then use the `bulk update` command with the CSV file path.

```bash
code42 trusted-activities bulk update update_trusted_activities.csv
```

```eval_rst
.. note::
    The ``bulk update`` command cannot be used to clear the description of a trusted activity because you cannot indicate an empty string in a CSV format.
    Pass an empty string to the ``description`` option of the ``update`` command to clear the description of a trusted activity.

    For example: ``code42 trusted-activities update 123 --description ""``
```

## Remove a Trusted Activity

Use the `remove` command to remove a single trusted activity.  Only the `resource_id` of an activity is required to remove it.

```bash
code42 trusted-activities remove 123
```

To remove multiple trusted activities at once, enter information about the trusted activity into the `remove` CSV file template, then use the `bulk remove` command with the CSV file path.

```bash
code42 trusted-activities bulk remove remove_trusted_activities.csv
```

Learn more about the [Trusted Activities](../commands/trustedactivities.md) commands.
