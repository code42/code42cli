# Manage Detection List Users

Use the `departing-employee` commands to add employees to or remove employees from the Departing Employees list. Use the `high-risk-employee` commands to add employees to or remove employees from the High Risk list, or update risk tags for those users.

To see a list of all the users currently in your organization, you can export a list from the
[Users action menu](https://support.code42.com/Administrator/Cloud/Administration_console_reference/Users_reference#Action_menu).

## Get CSV template
To add multiple users to the Departing Employees list:

1. Generate a CSV template. Below is an example command for generating a template to use to add employees to the Departing
Employees list. Once generated, the CSV file is saved to your current working directory.

```bash
code42 departing-employee bulk generate-template add
```

2. Use the CSV template to enter the employees' information. Only the Code42 username is required. If added,
the departure date must be in yyyy-MM-dd format. Note: you are only able to add departure dates during the `add`
operation. If you don't include `--departure-date`, you can only add one later by removing and then re-adding the
employee.

3. Save the CSV file.

## Add users to the Departing Employees list

Once you have entered the employees' information in the CSV file, use the `bulk add` command with the CSV file path to
add multiple users at once. For example:

```bash
code42 departing-employee bulk add /Users/astrid.ludwig/add_departing_employee.csv
```

## Remove users
You can remove one or more users from the High Risk Employees list. Use `code42 departing-employee remove` to remove a
single user.

To remove multiple users at once:

1. Create a CSV file with one username per line.

2. Save the file to your current working directory.

3. Use the `bulk remove` command. For example:

```bash
code42 high-risk-employee bulk remove /Users/matt.allen/remove_high_risk_employee.csv
```

Learn more about the [Departing Employee](../commands/departingemployee.md) and
[High Risk Employee](../commands/highriskemployee.md) commands.
