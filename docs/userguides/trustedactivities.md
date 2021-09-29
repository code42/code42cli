# Manage Trusted Activities

## Get CSV Template

The following command will generate a csv template to either create, update, or remove multiple trusted activities at once.  The csv file will be saved to the current working directory.
```bash
code42 trusted-activities bulk generate-template [create|update|remove]
```

Each of the CSV templates can then be filled out and used with their respective bulk command. 
```bash
code42 trusted-activities bulk [create|update|remove] Users/my_user/bulk-command.csv
```


For example, to create multiple trusted activities at once:

1. Generate a CSV template. Below is an example command for generating a template to use to create trusted activities. Once generated, the CSV file is saved to your current working directory.

```bash
code42 trusted-activities bulk generate-template create
```

2. Use the CSV template to enter each trusted activity's information. 
   The `type` and `value` fields are required. `type` indicates the category of activity, either `DOMAIN`, to indicate a trusted domain, or `SLACK`, to indicate a trusted Slack workspace.
   `value` indicates either name of the domain or Slack workspace, respectively.

3. Save the CSV file.

## Creating a New Trusted Activity

To update multiple trusted activites, enter the trusted activity's information in the CSV file, then use the `bulk create` command with the CSV file path. For example:

```bash
code42 trusted-activities bulk create /Users/my_user/create_trusted_activities.csv
```

Use the `create` command to create just a single trusted activity.
```bash
code42 trusted-activities create DOMAIN mydomain.com --description "a new trusted activity"
```

## Updating a Trusted Activity

Once you have entered the trusted activity's desired information in the CSV file, use the `bulk update` command with the CSV file path to
update multiple trusted activities at once. 

The `resource_id` of the activity is required for updating.  The other fields are optional.

For example:

```bash
code42 trusted-activities bulk update /Users/my_user/update_trusted_activities.csv
```

Use the `update` command to update just a single trusted activity.
```bash
code42 trusted-activities update 123 --value my-updated-domain.com --description "an updated trusted activity"
```

```eval_rst
.. important::
    Because there's no way to indicate an empty string in the CSV format, the `bulk update` command cannot be used to remove a trusted activity's description.  
    However, submitting an empty string to the regular `update` command will successfully clear the description.
    `code42 trusted-activities update 123 --description ""`
```


## Removing a Trusted Activity

Once you have entered the trusted activity's desired information in the CSV file, use the `bulk remove` command with the CSV file path to
remove multiple trusted activities at once.  

Only the `resource_id` of an activity is required to remove it.

```bash
code42 trusted-activities bulk remove /Users/my_user/remove_trusted_activities.csv
```

Use the `remove` command to remove just a single trusted activity.

```bash
code42 trusted-activities remove 123
```

Learn more about the [Trusted Activities](../commands/highriskemployee.md) commands.
