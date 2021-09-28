# Manage Trusted Activities

## Get CSV Template

The following command will generate a csv template to either create, update, or remove multiple trusted activities at once.  The csv file will be saved to the current working directory.
```bash
code42 trusted-activities bulk generate-template [create|update|remove]
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

## Create a New Trusted Activity

Once you have entered the trusted activity's information in the CSV file, use the `bulk create` command with the CSV file path to
create multiple trusted activities at once. For example:

```bash
code42 trusted-activities bulk create /Users/my_user/create_trusted_activities.csv
```

Use the `create` command to create just a single trusted activity.
```bash
code42 trusted-activities create DOMAIN mydomain.com --description "a new trusted activity"
```

## Update a Trusted Activity

Once you have entered the trusted activity's desired information in the CSV file, use the `bulk update` command with the CSV file path to
update multiple trusted activities at once. 

To update a trusted activity, the `resource_id` of the activity is required.  The other fields are optional.

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


## Remove a Trusted Activity
You can remove one or more users from the High Risk Employees list. Use `code42 departing-employee remove` to remove a
single user.

To remove multiple users at once:

1. Create a CSV file with one username per line.

2. Save the file to your current working directory.

3. Use the `bulk remove` command. For example:

```bash
code42 high-risk-employee bulk remove /Users/matt.allen/remove_high_risk_employee.csv
```

Learn more about the [Trusted Activities](../commands/trustedactivities.md) commands.
