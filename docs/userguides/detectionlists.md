# Managing Detection List Users

The Code42 command-line interface (CLI) tool offers a way to interact with your Code42 environment without using the 
Code42 console or making API calls directly. For example, you can use it to manage users on the 
[Departing Employees](https://support.code42.com/Administrator/Cloud/Administration_console_reference/Departing_Employees_reference) 
list or [High Risk Employees](https://support.code42.com/Administrator/Cloud/Administration_console_reference/High_Risk_Employees_reference) 
list. This article provides instructions for using the Code42 CLI to add and remove users 
from the Departing Employees list or High Risk Employees list, as well as update the information for a user. 

You can also use the Code42 CLI to extract Code42 data for use in a security information and event management (SIEM) 
tool. For more information, see [Integrate with a SIEM tool using the Code42 command-line interface](siemexample.md).

## Before you begin
To manage users on the Departing Employees list or High Risk Employees list with the Code42 CLI, you must first install 
and configure the Code42 CLI following the instructions in [Getting Started](gettingstarted.md). 

## Manage Departing Employees list users 
Use the departing-employee commands to add or remove employees on that that list, or update the details for a user. To 
see a list of all the users currently in your organization, you can export a list from the 
[Users action menu](https://support.code42.com/Administrator/Cloud/Administration_console_reference/Users_reference#Action_menu). 

## Get CSV template
To add multiple users to the Departing Employees list:

1. Generate a CSV template. Below is an example command for generating a template to use to add employees to the Departing 
Employees list. Once generated, the CSV file is saved to your current working directory.

```bash
code42 departing-employee bulk generate-template add
``` 

2. Use the CSV template to enter the employees' information. Only the Code42 username is required. If added, the departure 
date must be in YYYY-MM-DD format. 

3. Save the CSV file. 

## Add users to the Departing Employees list.

Once you have entered the employees' information in the CSV file, use the bulk add command with the CSV file path to 
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

3. Use the bulk remove command. For example:

```bash
code42 high-risk-employee bulk remove /Users/matt.allen/remove_high_risk_employee.csv
```

Learn more about the [Departing Employee](../commands/departingemployee.md) and the 
[High Risk Employee](../commands/highriskemployee.md) commands.
